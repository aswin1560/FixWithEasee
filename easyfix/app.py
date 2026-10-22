"""
AI-Powered Local Skill Connect
Main Flask Application Entry Point
"""

import os
import time
from functools import wraps
from flask import (
    Flask, render_template, request, session, redirect,
    url_for, flash, jsonify
)
from dotenv import load_dotenv

from models.user import (
    create_user, get_user_by_email, get_user_by_id, verify_user_password
)
from models.worker import (
    create_worker, get_all_workers, get_worker_by_user_id, search_workers
)
from models.subscription import (
    is_subscribed, get_user_subscription, create_or_extend_subscription
)
from models.order import (
    create_order, get_order_by_id, get_orders_by_customer, get_admin_dashboard_data, update_order_status
)
from models.review import (
    create_review, get_review_by_order_id, get_reviews_for_worker
)
from services.location import (
    haversine_distance, DEFAULT_CHENNAI_LAT, DEFAULT_CHENNAI_LNG
)
from services.ai_matcher import (
    analyze_problem_with_gemini, score_and_rank_workers
)
from services.diy_tutor import get_diy_tutorial
from services.payment_service import (
    create_razorpay_order, verify_razorpay_payment, generate_test_signature
)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "easyfix-secret-key-development")


# ==============================================================================
# Context Processor (Global Template Variables)
# ==============================================================================
@app.context_processor
def inject_global_data():
    """Injects user subscription state into all templates."""
    user_id = session.get("user_id")
    subscribed = is_subscribed(user_id) if user_id else False
    return {
        "user_is_subscribed": subscribed,
        "current_user_id": user_id,
        "current_user_name": session.get("user_name"),
        "current_user_role": session.get("user_role")
    }


# ==============================================================================
# Authentication & Authorization Decorators
# ==============================================================================
def login_required(f):
    """Decorator ensuring that the user is authenticated in session."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def subscription_required(f):
    """
    Decorator ensuring the user has an ACTIVE subscription.
    ALWAYS checked on the server. Returns 403 if not subscribed.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get("user_id")
        # If user is not logged in at all, prompt login
        if not user_id:
            flash("Please log in to access this feature.", "warning")
            return redirect(url_for("login", next=request.url))

        # Server-side subscription check
        if not is_subscribed(user_id):
            if request.is_json or request.path.startswith("/api/"):
                return jsonify({
                    "error": "Subscription Required",
                    "message": "Subscribe to unlock AI-powered features."
                }), 403
            return render_template("subscription_required.html"), 403

        return f(*args, **kwargs)
    return decorated_function


# ==============================================================================
# Public Routes
# ==============================================================================
@app.route("/")
def index():
    """Home page route displaying search, features, and pricing banner."""
    return render_template("index.html")


@app.route("/pricing")
def pricing():
    """Pricing page showing ₹30/mo and ₹300/yr plans, benefits, and yearly savings."""
    return render_template("pricing.html")


# ==============================================================================
# Authentication Routes (Register / Login / Logout)
# ==============================================================================
@app.route("/register", methods=["GET", "POST"])
def register():
    """Handles new user registration for both customers and workers."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "customer").strip()
        city = request.form.get("city", "Chennai").strip()
        lat = request.form.get("lat")
        lng = request.form.get("lng")

        # Basic validations
        if not name or not email or not password:
            flash("Please fill in all required fields.", "danger")
            return render_template("register.html"), 400

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template("register.html"), 400

        if get_user_by_email(email):
            flash("An account with that email already exists. Please log in.", "danger")
            return render_template("register.html"), 400

        try:
            lat_float = float(lat) if lat else 13.0827
            lng_float = float(lng) if lng else 80.2707
        except ValueError:
            lat_float, lng_float = 13.0827, 80.2707

        # Create user record
        user_id = create_user(
            name=name,
            email=email,
            password=password,
            role=role,
            city=city,
            lat=lat_float,
            lng=lng_float
        )

        # If registering as a worker, also create worker profile
        if role == "worker":
            skills = request.form.get("skills", "General Maintenance").strip()
            try:
                experience = int(request.form.get("experience_years", 1))
            except ValueError:
                experience = 1
            create_worker(
                user_id=user_id,
                skills=skills,
                experience_years=experience,
                rating_avg=5.0,
                is_available=1,
                verified=1
            )

        # Log user into session
        session["user_id"] = user_id
        session["user_name"] = name
        session["user_role"] = role
        session["user_email"] = email

        flash(f"Welcome to FixWithEase, {name}! Your account is ready.", "success")
        return redirect(url_for("index"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Handles user authentication with hashed password verification."""
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        next_url = request.form.get("next") or request.args.get("next")

        user = get_user_by_email(email)
        if not user or not verify_user_password(user, password):
            flash("Invalid email or password. Please try again.", "danger")
            return render_template("login.html"), 401

        # Establish session
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        session["user_role"] = user["role"]
        session["user_email"] = user["email"]

        flash(f"Welcome back, {user['name']}!", "success")
        if next_url and next_url.startswith("/"):
            return redirect(next_url)
        return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Clears session and logs user out."""
    session.clear()
    flash("You have been successfully logged out.", "info")
    return redirect(url_for("index"))


# ==============================================================================
# Subscription Management (Mock Subscribe for Phase 3)
# ==============================================================================
@app.route("/subscribe", methods=["POST"])
@login_required
def subscribe():
    """
    Mock subscription creator (Phase 3).
    Creates or extends a subscription row in the database.
    (Real Razorpay payment gateway integration will be in Phase 7).
    """
    plan = request.form.get("plan", "monthly")
    if plan not in ["monthly", "yearly"]:
        plan = "monthly"

    days = 365 if plan == "yearly" else 30
    create_or_extend_subscription(session["user_id"], plan=plan, days=days)

    flash(f"🎉 Congratulations! You have successfully subscribed to the {plan.capitalize()} plan. AI features and 0% booking fees are now unlocked!", "success")
    return redirect(url_for("pricing"))


# ==============================================================================
# Razorpay TEST Mode Payment Endpoints (Phase 7)
# ==============================================================================
@app.route("/create-razorpay-order", methods=["POST"])
@login_required
def create_razorpay_order_api():
    """Creates a Razorpay TEST mode order for Monthly (₹30) or Yearly (₹300) plan."""
    data = request.get_json(silent=True) or request.form
    plan = data.get("plan", "monthly")
    order = create_razorpay_order(plan=plan)
    return jsonify(order)


@app.route("/simulate-payment-signature", methods=["POST"])
@login_required
def simulate_payment_signature():
    """Generates a valid test signature for offline/local simulation testing."""
    data = request.get_json(silent=True) or request.form
    order_id = data.get("order_id", f"order_test_{int(time.time())}")
    payment_id = f"pay_test_{int(time.time())}"
    signature = generate_test_signature(order_id, payment_id)
    return jsonify({
        "order_id": order_id,
        "payment_id": payment_id,
        "signature": signature
    })


@app.route("/verify-payment", methods=["POST"])
@login_required
def verify_payment_api():
    """
    Verifies the Razorpay payment signature on the server using HMAC SHA256.
    If valid, activates or extends the customer's subscription.
    """
    data = request.get_json(silent=True) or request.form
    order_id = data.get("razorpay_order_id")
    payment_id = data.get("razorpay_payment_id")
    signature = data.get("razorpay_signature")
    plan = data.get("plan", "monthly")

    # Server-side cryptographic signature verification
    is_valid = verify_razorpay_payment(order_id, payment_id, signature)
    if not is_valid:
        return jsonify({
            "success": False,
            "message": "Payment signature verification failed. Untrusted or tampered transaction."
        }), 400

    # Payment verified -> activate/extend subscription
    days = 365 if plan == "yearly" else 30
    create_or_extend_subscription(session["user_id"], plan=plan, days=days)

    return jsonify({
        "success": True,
        "message": f"Payment of ₹{300 if plan == 'yearly' else 30} verified! Your {plan.capitalize()} subscription is now active."
    })


# ==============================================================================
# Admin Dashboard (Phase 7)
# ==============================================================================
@app.route("/admin")
def admin_dashboard():
    """
    Admin dashboard displaying:
    - Total subscription revenue
    - Total 5% consulting fee revenue
    - Total combined revenue and order records
    """
    # Enforce admin privilege
    if session.get("user_role") != "admin" and session.get("user_email") != "admin@example.com":
        flash("Admin access required. Please log in with an administrator account.", "warning")
        return redirect(url_for("login", next=url_for("admin_dashboard")))

    data = get_admin_dashboard_data()
    return render_template("admin.html", data=data)


# ==============================================================================
# Workers Directory & Booking Flow (Phase 4)
# ==============================================================================
@app.route("/workers")
def workers():
    """
    Worker directory search with keyword, skill, and city filters (Phase 4).
    Calculates Haversine distance from the customer's coordinates.
    """
    query = request.args.get("q", "").strip()
    skill = request.args.get("skill", "").strip()
    city = request.args.get("city", "").strip()
    available_only = request.args.get("available") in ["1", "true", "on"]

    # Customer coordinates from query params or user session
    user_lat = request.args.get("lat")
    user_lng = request.args.get("lng")

    if not user_lat or not user_lng:
        user_id = session.get("user_id")
        if user_id:
            user_rec = get_user_by_id(user_id)
            if user_rec and user_rec["lat"] and user_rec["lng"]:
                user_lat, user_lng = user_rec["lat"], user_rec["lng"]

    # Fallback to Chennai center for distance estimation
    try:
        calc_lat = float(user_lat) if user_lat else DEFAULT_CHENNAI_LAT
        calc_lng = float(user_lng) if user_lng else DEFAULT_CHENNAI_LNG
    except ValueError:
        calc_lat, calc_lng = DEFAULT_CHENNAI_LAT, DEFAULT_CHENNAI_LNG

    # Pure SQL LIKE search (no AI)
    raw_workers = search_workers(
        keyword=query if query else None,
        skill=skill if skill else None,
        city=city if city else None,
        available_only=available_only
    )

    # Attach calculated distance to each worker
    worker_list = []
    for w in raw_workers:
        w_dict = dict(w)
        dist = haversine_distance(calc_lat, calc_lng, w_dict.get("lat"), w_dict.get("lng"))
        w_dict["distance_km"] = dist
        worker_list.append(w_dict)

    return render_template(
        "workers.html",
        workers=worker_list,
        query=query,
        selected_skill=skill,
        selected_city=city,
        available_only=available_only,
        user_lat=user_lat,
        user_lng=user_lng
    )


@app.route("/book/<int:worker_id>", methods=["GET", "POST"])
@login_required
def book_worker(worker_id):
    """
    Booking page and order creation (Phase 4).
    Applies 5% consulting fee for free users, 0% fee for subscribers.
    """
    worker = get_worker_by_user_id(worker_id)
    if not worker:
        flash("Worker not found.", "danger")
        return redirect(url_for("workers"))

    user_id = session["user_id"]
    user_subscribed = is_subscribed(user_id)

    if request.method == "POST":
        problem_text = request.form.get("problem_text", "").strip()
        try:
            base_amount = float(request.form.get("base_amount", 350.0))
        except ValueError:
            base_amount = 350.0

        if not problem_text:
            flash("Please provide a description of the problem.", "danger")
            return render_template("book.html", worker=worker)

        # 5% fee for free users, 0% fee for active subscribers
        if user_subscribed:
            fee_amount = 0.0
        else:
            fee_amount = round(base_amount * 0.05, 2)

        order_id = create_order(
            customer_id=user_id,
            worker_id=worker_id,
            problem_text=problem_text,
            base_amount=base_amount,
            fee_amount=fee_amount
        )

        flash(f"Order #{order_id} placed successfully!", "success")
        return redirect(url_for("order_detail", order_id=order_id))

    return render_template("book.html", worker=worker)


@app.route("/orders/<int:order_id>")
@login_required
def order_detail(order_id):
    """Displays order confirmation, payment breakdown, and reviews."""
    order = get_order_by_id(order_id)
    if not order:
        flash("Order not found.", "danger")
        return redirect(url_for("workers"))

    review = get_review_by_order_id(order_id)
    return render_template("order_detail.html", order=order, review=review)


@app.route("/orders/<int:order_id>/complete", methods=["POST"])
@login_required
def complete_order(order_id):
    """Marks an active order as completed so the customer can review the worker."""
    order = get_order_by_id(order_id)
    if not order:
        flash("Order not found.", "danger")
        return redirect(url_for("workers"))

    update_order_status(order_id, "completed")
    flash("Order marked as completed! You can now leave a rating and review.", "success")
    return redirect(url_for("order_detail", order_id=order_id))


@app.route("/orders/<int:order_id>/review", methods=["POST"])
@login_required
def submit_review(order_id):
    """Submits a star rating and comment for a completed order, updating worker rating."""
    order = get_order_by_id(order_id)
    if not order:
        flash("Order not found.", "danger")
        return redirect(url_for("workers"))

    rating = request.form.get("rating", "5")
    comment = request.form.get("comment", "").strip()

    try:
        rating_int = int(rating)
    except ValueError:
        rating_int = 5

    create_review(order_id=order_id, rating=rating_int, comment=comment)
    flash("Thank you! Your review has been submitted and the worker's average rating updated.", "success")
    return redirect(url_for("order_detail", order_id=order_id))


@app.route("/my-orders")
@login_required
def my_orders():
    """Lists all orders placed by the current logged-in customer."""
    customer_id = session["user_id"]
    orders = get_orders_by_customer(customer_id)
    return render_template("my_orders.html", orders=orders)


# ==============================================================================
# Protected AI Routes (Phase 5 & 6)
# ==============================================================================
@app.route("/fix", methods=["GET", "POST"])
@subscription_required
def fix():
    """
    Fix It Yourself DIY helper (Phase 6).
    PROTECTED: Requires active subscription.
    Checks keyword blocklist + AI safety filter.
    Refuses risky tasks and offers matching workers instead.
    """
    query = ""
    if request.method == "POST":
        query = request.form.get("q", "").strip()
    else:
        query = request.args.get("q", "").strip()

    tutorial = None
    if query:
        tutorial = get_diy_tutorial(query)

    return render_template("fix.html", query=query, tutorial=tutorial)


@app.route("/api/fix", methods=["POST"])
@subscription_required
def api_fix():
    """
    API endpoint for Fix It Yourself tutorial.
    Returns JSON response containing tutorial or safety refusal.
    """
    data = request.get_json(silent=True) or request.form
    problem_text = data.get("problem_text") or data.get("q") or ""

    if not problem_text.strip():
        return jsonify({
            "error": "Bad Request",
            "message": "Problem description is required."
        }), 400

    tutorial = get_diy_tutorial(problem_text)
    return jsonify(tutorial)


# ==============================================================================
# AI Search Routes (Phase 5 - Subscribers Only)
# ==============================================================================
@app.route("/ai-search", methods=["GET", "POST"])
@subscription_required
def ai_search():
    """
    AI-Powered Problem Matcher (Phase 5).
    PROTECTED: Requires active subscription (checked on server).
    Customer enters problem in plain words, Gemini AI analyzes it,
    and workers are scored and ranked.
    """
    query = ""
    if request.method == "POST":
        query = request.form.get("q", "").strip()
    else:
        query = request.args.get("q", "").strip()

    user_lat = request.args.get("lat") or request.form.get("lat")
    user_lng = request.args.get("lng") or request.form.get("lng")

    if not user_lat or not user_lng:
        user_id = session.get("user_id")
        if user_id:
            user_rec = get_user_by_id(user_id)
            if user_rec and user_rec["lat"] and user_rec["lng"]:
                user_lat, user_lng = user_rec["lat"], user_rec["lng"]

    analysis = None
    ranked_workers = []

    if query:
        # Step 1 & 2: Analyze problem with Gemini (or safe fallback)
        analysis = analyze_problem_with_gemini(query)
        # Step 3 & 4: Score and rank top 5 workers
        ranked_workers = score_and_rank_workers(analysis, customer_lat=user_lat, customer_lng=user_lng)

    return render_template(
        "ai_search.html",
        query=query,
        analysis=analysis,
        ranked_workers=ranked_workers,
        user_lat=user_lat,
        user_lng=user_lng
    )


@app.route("/api/ai/match", methods=["POST"])
@subscription_required
def ai_match():
    """
    AI Problem Matcher API (Phase 5).
    PROTECTED: Requires active subscription. Returns JSON with diagnosis and ranked workers.
    """
    data = request.get_json(silent=True) or request.form
    problem_text = data.get("problem_text") or data.get("q") or ""

    if not problem_text.strip():
        problem_text = "general home maintenance"

    user_lat = data.get("lat")
    user_lng = data.get("lng")

    if not user_lat or not user_lng:
        user_id = session.get("user_id")
        if user_id:
            user_rec = get_user_by_id(user_id)
            if user_rec and user_rec["lat"] and user_rec["lng"]:
                user_lat, user_lng = user_rec["lat"], user_rec["lng"]

    analysis = analyze_problem_with_gemini(problem_text)
    ranked_workers = score_and_rank_workers(analysis, customer_lat=user_lat, customer_lng=user_lng)

    return jsonify({
        "status": "success",
        "analysis": analysis,
        "ranked_workers": ranked_workers
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=True)
