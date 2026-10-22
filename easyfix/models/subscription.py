"""
Subscription Model and Helper Functions
Handles subscription creation, validation, and status checks on the server.
"""

from datetime import datetime, timedelta
from models.db import get_db_connection


def create_or_extend_subscription(user_id, plan="monthly", days=None):
    """
    Creates a new subscription or extends an active subscription for a user.
    Monthly = 30 days, Yearly = 365 days.
    """
    if days is None:
        days = 365 if plan == "yearly" else 30

    now = datetime.now()
    existing = get_user_subscription(user_id)

    # If already active and end_date is in the future, extend from that end_date
    if existing and existing["status"] == "active":
        try:
            current_end = datetime.fromisoformat(existing["end_date"])
            if current_end > now:
                start_date = existing["start_date"]
                end_date = (current_end + timedelta(days=days)).isoformat()
            else:
                start_date = now.isoformat()
                end_date = (now + timedelta(days=days)).isoformat()
        except ValueError:
            start_date = now.isoformat()
            end_date = (now + timedelta(days=days)).isoformat()
    else:
        start_date = now.isoformat()
        end_date = (now + timedelta(days=days)).isoformat()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO subscriptions (user_id, plan, start_date, end_date, status)
        VALUES (?, ?, ?, ?, 'active')
    """, (user_id, plan, start_date, end_date))
    sub_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return sub_id


def get_user_subscription(user_id):
    """
    Fetches the latest subscription record for a user.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM subscriptions 
        WHERE user_id = ? 
        ORDER BY id DESC 
        LIMIT 1
    """, (user_id,))
    sub = cursor.fetchone()
    conn.close()
    return sub


def is_subscribed(user_id):
    """
    Checks if a user has an active, non-expired subscription.
    ALWAYS verified on the server.
    """
    if not user_id:
        return False

    sub = get_user_subscription(user_id)
    if not sub:
        return False

    if sub["status"] != "active":
        return False

    try:
        end_date = datetime.fromisoformat(sub["end_date"])
        # If current time is before the end date, subscription is valid
        return datetime.now() <= end_date
    except (ValueError, TypeError):
        return False
