"""
AI Worker Matcher Service
Analyzes customer problem descriptions using Google Gemini AI,
validates the output JSON safely, falls back to intelligent keyword analysis,
and scores/ranks workers by skill match, distance, rating, availability, and past orders.
"""

import os
import re
import json
import logging
from dotenv import load_dotenv
from services.location import haversine_distance, DEFAULT_CHENNAI_LAT, DEFAULT_CHENNAI_LNG
from models.db import get_db_connection

load_dotenv()
logger = logging.getLogger(__name__)

# Risky categories per project rules:
# electrical wiring, sockets, switchboards, MCB/fuse, gas (LPG) lines and cylinders,
# water heaters/geysers, structural or wall-cutting work, roof/height work, fire, chemicals.
RISKY_PATTERNS = [
    r"\b(spark|sparking|shock|short\s*circuit|electrocute|current)\b",
    r"\b(wiring|wire|switchboard|mcb|fuse|main\s*board|meter\s*board)\b",
    r"\b(gas|lpg|cylinder|gas\s*leak|burner\s*leak)\b",
    r"\b(geyser|water\s*heater|boiler)\b",
    r"\b(structural|wall\s*cutting|demolition|pillar|beam)\b",
    r"\b(roof|height|terrace\s*edge|scaffolding)\b",
    r"\b(chemical|acid|fire|flame|explosion)\b"
]


def check_is_risky(text):
    """Checks whether the problem description contains hazardous keywords."""
    lowered = text.lower()
    for pattern in RISKY_PATTERNS:
        if re.search(pattern, lowered):
            return True
    return False


def fallback_problem_analyzer(problem_text):
    """
    Intelligent fallback heuristic parser used when Gemini API key is missing,
    invalid, quota-limited, or network fails.
    """
    text = problem_text.lower()
    is_risky = check_is_risky(text)

    # Determine skill needed
    if any(k in text for k in ["tap", "leak", "pipe", "water", "sink", "drain", "flush", "toilet", "clog", "faucet", "plumb"]):
        skill_needed = "Plumber"
        summary = "Plumbing issue involving water flow, leakage, or fixture repairs."
    elif any(k in text for k in ["fan", "wire", "switch", "light", "mcb", "fuse", "power", "plug", "socket", "electric", "short", "shock", "spark"]):
        skill_needed = "Electrician"
        summary = "Electrical issue involving power supply, wiring, fan, or switchboards."
    elif any(k in text for k in ["table", "chair", "door", "lock", "hinge", "wood", "cabinet", "furniture", "drawer", "carpent"]):
        skill_needed = "Carpenter"
        summary = "Carpentry repair involving furniture, woodwork, door locks, or hinges."
    elif any(k in text for k in ["paint", "putty", "wall", "color", "damp", "whitewash", "stain"]):
        skill_needed = "Painter"
        summary = "Painting, wall surface preparation, or touch-up work."
    elif any(k in text for k in ["ac", "air conditioner", "cooling", "cool", "compressor"]):
        skill_needed = "AC Repair"
        summary = "Air conditioning diagnosis, filter cleaning, or cooling repair."
    elif any(k in text for k in ["washing machine", "fridge", "refrigerator", "microwave", "mixer", "grinder", "appliance"]):
        skill_needed = "Appliance Repair"
        summary = "Home appliance repair and maintenance."
    else:
        skill_needed = "Plumber"  # Default fallback
        summary = f"General home maintenance for: {problem_text[:50]}"

    # Determine urgency
    if any(k in text for k in ["emergency", "urgent", "burst", "flood", "shock", "fire", "spark", "heavy leak"]):
        urgency = "high"
    elif any(k in text for k in ["paint", "polish", "loose", "creak", "squeak", "minor"]):
        urgency = "low"
    else:
        urgency = "medium"

    return {
        "skill_needed": skill_needed,
        "urgency": urgency,
        "summary": summary,
        "is_risky": is_risky,
        "source": "heuristic_fallback"
    }


def analyze_problem_with_gemini(problem_text):
    """
    Sends the customer's problem description to Google Gemini AI
    and requests structured JSON: {skill_needed, urgency, summary, is_risky}.
    Falls back gracefully if the API is unavailable.
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    # If no key or dummy placeholder, use safe heuristic fallback
    if not api_key or api_key == "your_gemini_api_key_here":
        return fallback_problem_analyzer(problem_text)

    prompt = f"""
You are an expert home repair intake AI. Analyze this customer's problem description:
"{problem_text}"

Respond with ONLY a raw JSON object (no markdown, no backticks, no explanatory text) with these exact keys:
{{
  "skill_needed": "<one of: Plumber, Electrician, Carpenter, Painter, AC Repair, Appliance Repair>",
  "urgency": "<one of: low, medium, high>",
  "summary": "<one sentence concise description of the issue>",
  "is_risky": <true if the work involves electrical wiring/sockets/MCB, gas/LPG, water heaters/geysers, wall-cutting/structural, heights/roof, fire or chemicals; otherwise false>
}}
"""

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        raw_text = response.text.strip()

        # Clean markdown code fences if present (e.g. ```json ... ```)
        cleaned_text = re.sub(r"^```(?:json)?\s*", "", raw_text, flags=re.IGNORECASE)
        cleaned_text = re.sub(r"\s*```$", "", cleaned_text).strip()

        data = json.loads(cleaned_text)

        # Validate required JSON keys
        required_keys = ["skill_needed", "urgency", "summary", "is_risky"]
        if not all(k in data for k in required_keys):
            logger.warning("Gemini JSON missing required keys, using fallback.")
            return fallback_problem_analyzer(problem_text)

        # Ensure safety rule: also cross-check against keyword blocklist
        if check_is_risky(problem_text):
            data["is_risky"] = True

        data["source"] = "gemini_ai"
        return data

    except Exception as e:
        logger.warning(f"Gemini API call failed ({e}), using safe fallback.")
        return fallback_problem_analyzer(problem_text)


def score_and_rank_workers(problem_analysis, customer_lat=None, customer_lng=None):
    """
    Scores and ranks all workers based on:
    1. Skill match (highest weight: up to 50 pts)
    2. Proximity / Distance (up to 20 pts)
    3. Rating average (up to 15 pts)
    4. Availability status (up to 10 pts)
    5. Past completed orders (up to 5 pts)

    Returns top 5 ranked workers with short reason for each.
    """
    target_skill = problem_analysis.get("skill_needed", "Plumber")

    # Fallback to Chennai center if coordinates are missing
    try:
        c_lat = float(customer_lat) if customer_lat else DEFAULT_CHENNAI_LAT
        c_lng = float(customer_lng) if customer_lng else DEFAULT_CHENNAI_LNG
    except ValueError:
        c_lat, c_lng = DEFAULT_CHENNAI_LAT, DEFAULT_CHENNAI_LNG

    conn = get_db_connection()
    cursor = conn.cursor()
    # Fetch all workers joined with user profile and count of completed orders
    cursor.execute("""
        SELECT 
            w.user_id,
            u.name,
            u.email,
            u.city,
            u.lat,
            u.lng,
            w.skills,
            w.experience_years,
            w.rating_avg,
            w.is_available,
            w.verified,
            (SELECT COUNT(*) FROM orders o WHERE o.worker_id = w.user_id AND o.status = 'completed') AS completed_orders
        FROM workers w
        JOIN users u ON w.user_id = u.id
    """)
    raw_workers = cursor.fetchall()
    conn.close()

    scored_workers = []

    for w in raw_workers:
        w_dict = dict(w)
        skills_str = w_dict["skills"]

        # 1. Skill Match Score (Max 50 points)
        if target_skill.lower() in skills_str.lower():
            skill_score = 50.0
        else:
            # Check secondary tokens
            skill_score = 10.0

        # 2. Distance Score (Max 20 points)
        dist = haversine_distance(c_lat, c_lng, w_dict.get("lat"), w_dict.get("lng"))
        if dist is None:
            dist = 5.0  # reasonable default

        if dist <= 2.0:
            dist_score = 20.0
        elif dist <= 5.0:
            dist_score = 16.0
        elif dist <= 10.0:
            dist_score = 12.0
        elif dist <= 20.0:
            dist_score = 6.0
        else:
            dist_score = 2.0

        # 3. Rating Score (Max 15 points)
        rating = float(w_dict["rating_avg"] or 5.0)
        rating_score = round((rating / 5.0) * 15.0, 1)

        # 4. Availability Score (Max 10 points)
        is_avail = bool(w_dict["is_available"])
        avail_score = 10.0 if is_avail else 0.0

        # 5. Past Completed Orders Score (Max 5 points)
        completed = int(w_dict["completed_orders"] or 0)
        orders_score = min(5.0, completed * 2.5)

        # Total Match Score (out of 100)
        total_score = round(skill_score + dist_score + rating_score + avail_score + orders_score, 1)

        # Generate recommendation reason (e.g. 'Plumber, 2 km away, 4.8 rating')
        avail_text = "Available Now" if is_avail else "Busy"
        reason = f"{target_skill}, {dist} km away, {rating} rating, {avail_text}"

        w_dict["distance_km"] = dist
        w_dict["match_score"] = total_score
        w_dict["recommendation_reason"] = reason

        scored_workers.append(w_dict)

    # Sort descending by total match score
    scored_workers.sort(key=lambda x: x["match_score"], reverse=True)

    # Return top 5 ranked workers
    return scored_workers[:5]
