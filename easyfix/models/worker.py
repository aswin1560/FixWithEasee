"""
Worker Model and Helper Functions
Handles worker profile creation, lookup, and search queries.
"""

from models.db import get_db_connection


def create_worker(user_id, skills, experience_years=1, rating_avg=5.0, is_available=1, verified=1):
    """Inserts a new worker profile linked to an existing user record."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO workers (user_id, skills, experience_years, rating_avg, is_available, verified)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, skills, experience_years, rating_avg, is_available, verified))
    conn.commit()
    conn.close()


def get_worker_by_user_id(user_id):
    """Fetches complete worker profile joined with user account details."""
    conn = get_db_connection()
    cursor = conn.cursor()
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
            w.verified
        FROM workers w
        JOIN users u ON w.user_id = u.id
        WHERE w.user_id = ?
    """, (user_id,))
    worker = cursor.fetchone()
    conn.close()
    return worker


def get_all_workers(available_only=False):
    """Returns all workers joined with user details."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
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
            w.verified
        FROM workers w
        JOIN users u ON w.user_id = u.id
    """
    params = []
    if available_only:
        query += " WHERE w.is_available = 1"
    query += " ORDER BY w.rating_avg DESC"

    cursor.execute(query, params)
    workers = cursor.fetchall()
    conn.close()
    return workers


def search_workers(keyword=None, skill=None, city=None, available_only=False):
    """
    Basic SQL LIKE search for Phase 4 (free tier).
    Searches across skills, city, and worker names.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
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
            w.verified
        FROM workers w
        JOIN users u ON w.user_id = u.id
        WHERE 1=1
    """
    params = []

    if keyword:
        query += " AND (w.skills LIKE ? OR u.name LIKE ? OR u.city LIKE ?)"
        wildcard = f"%{keyword.strip()}%"
        params.extend([wildcard, wildcard, wildcard])

    if skill:
        query += " AND w.skills LIKE ?"
        params.append(f"%{skill.strip()}%")

    if city:
        query += " AND u.city LIKE ?"
        params.append(f"%{city.strip()}%")

    if available_only:
        query += " AND w.is_available = 1"

    query += " ORDER BY w.rating_avg DESC"

    cursor.execute(query, params)
    workers = cursor.fetchall()
    conn.close()
    return workers


def update_worker_rating(user_id):
    """
    Recalculates and updates the worker's rating_avg
    based on all completed order reviews.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT AVG(r.rating) as avg_rating
        FROM reviews r
        JOIN orders o ON r.order_id = o.id
        WHERE o.worker_id = ?
    """, (user_id,))
    result = cursor.fetchone()
    if result and result["avg_rating"] is not None:
        new_avg = round(float(result["avg_rating"]), 2)
        cursor.execute("UPDATE workers SET rating_avg = ? WHERE user_id = ?", (new_avg, user_id))
        conn.commit()
    conn.close()
