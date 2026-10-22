"""
Payment Service for AI-Powered Local Skill Connect
Handles Razorpay TEST mode integration for:
- ₹30 Monthly subscription (3,000 paise)
- ₹300 Yearly subscription (30,000 paise)
- HMAC SHA256 server-side signature verification
- 5% consulting fee calculation
"""

import os
import hmac
import hashlib
import time
import razorpay
from dotenv import load_dotenv

load_dotenv()

# Subscription plan amounts in Indian Paise (1 Rupee = 100 Paise)
PLAN_AMOUNTS = {
    "monthly": {
        "amount_rupees": 30,
        "amount_paise": 3000,
        "days": 30,
        "name": "FixWithEase Pro - Monthly"
    },
    "yearly": {
        "amount_rupees": 300,
        "amount_paise": 30000,
        "days": 365,
        "name": "FixWithEase Pro - Yearly (2 Months Free)"
    }
}


def get_razorpay_credentials():
    """Retrieves Razorpay key and secret from environment."""
    key_id = os.getenv("RAZORPAY_KEY_ID", "rzp_test_placeholder")
    key_secret = os.getenv("RAZORPAY_KEY_SECRET", "rzp_secret_placeholder")
    return key_id, key_secret


def create_razorpay_order(plan="monthly"):
    """
    Creates a Razorpay order in test mode.
    Returns order details dict with order_id, amount, currency, and key_id.
    """
    if plan not in PLAN_AMOUNTS:
        plan = "monthly"

    plan_info = PLAN_AMOUNTS[plan]
    amount_paise = plan_info["amount_paise"]
    key_id, key_secret = get_razorpay_credentials()

    receipt_id = f"rcpt_{plan}_{int(time.time())}"

    # If active test keys are provided, call Razorpay API
    if key_id != "rzp_test_placeholder" and not key_id.startswith("rzp_test_placeholder"):
        try:
            client = razorpay.Client(auth=(key_id, key_secret))
            order_data = {
                "amount": amount_paise,
                "currency": "INR",
                "receipt": receipt_id,
                "notes": {"plan": plan}
            }
            rzp_order = client.order.create(data=order_data)
            return {
                "success": True,
                "order_id": rzp_order["id"],
                "amount": amount_paise,
                "currency": "INR",
                "key_id": key_id,
                "plan": plan,
                "plan_name": plan_info["name"]
            }
        except Exception:
            # Fall back to test simulator if network/auth fails
            pass

    # Simulated Test Mode Order ID
    simulated_order_id = f"order_test_{plan}_{int(time.time())}"
    return {
        "success": True,
        "order_id": simulated_order_id,
        "amount": amount_paise,
        "currency": "INR",
        "key_id": key_id,
        "plan": plan,
        "plan_name": plan_info["name"]
    }


def verify_razorpay_payment(order_id, payment_id, signature):
    """
    Verifies Razorpay payment signature on the server using HMAC SHA256.
    Ensures payment was genuinely authorized and untampered.
    """
    if not order_id or not payment_id or not signature:
        return False

    key_id, key_secret = get_razorpay_credentials()

    try:
        # Standard Razorpay HMAC-SHA256 signature verification
        msg = f"{order_id}|{payment_id}".encode("utf-8")
        expected_signature = hmac.new(
            key_secret.encode("utf-8"),
            msg,
            hashlib.sha256
        ).hexdigest()

        # Constant-time comparison to prevent timing attacks
        return hmac.compare_digest(expected_signature, signature)
    except Exception:
        return False


def generate_test_signature(order_id, payment_id):
    """Helper to generate a valid test signature for unit tests and local simulation."""
    _, key_secret = get_razorpay_credentials()
    msg = f"{order_id}|{payment_id}".encode("utf-8")
    return hmac.new(key_secret.encode("utf-8"), msg, hashlib.sha256).hexdigest()


def calculate_consulting_fee(base_amount, is_user_subscribed):
    """
    Calculates order consulting fee:
    - 0% (₹0.00) for subscribed users
    - 5% of base_amount for free (unsubscribed) users
    """
    try:
        amount = float(base_amount)
    except (ValueError, TypeError):
        amount = 0.0

    if is_user_subscribed:
        return 0.0
    return round(amount * 0.05, 2)
