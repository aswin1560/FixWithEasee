"""
User Model and Helper Functions
Handles user creation, lookup, and password hashing/verification.
"""

from werkzeug.security import generate_password_hash, check_password_hash
from models.db import get_db_connection


def create_user(name, email, password, role="customer", city="Chennai", lat=None, lng=None):
    """
    Creates a new user record with a hashed password.
    Returns the new user's ID.
    """
    password_hash = generate_password_hash(password)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (name, email, password_hash, role, city, lat, lng)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, email.strip().lower(), password_hash, role, city, lat, lng))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id


def get_user_by_email(email):
    """Fetches a single user by their email address."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE LOWER(email) = LOWER(?)", (email.strip(),))
    user = cursor.fetchone()
    conn.close()
    return user


def get_user_by_id(user_id):
    """Fetches a single user by their primary key ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user


def verify_user_password(user, password):
    """Verifies a plain password against the stored password hash."""
    if not user or not user["password_hash"]:
        return False
    return check_password_hash(user["password_hash"], password)
