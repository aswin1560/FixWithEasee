"""
Review Model and Helper Functions
Handles reviews and customer ratings for completed orders.
"""

from models.db import get_db_connection
from models.worker import update_worker_rating


def create_review(order_id, rating, comment=None):
    """
    Inserts a review for an order and triggers a recalculation of the worker's average rating.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO reviews (order_id, rating, comment)
        VALUES (?, ?, ?)
    """, (order_id, int(rating), comment.strip() if comment else None))
    conn.commit()

    # Find the worker_id for this order to update their rating
    cursor.execute("SELECT worker_id FROM orders WHERE id = ?", (order_id,))
    order = cursor.fetchone()
    conn.close()

    if order:
        update_worker_rating(order["worker_id"])


def get_review_by_order_id(order_id):
    """Fetches a review by its associated order ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reviews WHERE order_id = ?", (order_id,))
    review = cursor.fetchone()
    conn.close()
    return review


def get_reviews_for_worker(worker_id):
    """Fetches all reviews left for a specific worker."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            r.*,
            c.name AS customer_name,
            o.problem_text
        FROM reviews r
        JOIN orders o ON r.order_id = o.id
        JOIN users c ON o.customer_id = c.id
        WHERE o.worker_id = ?
        ORDER BY r.created_at DESC
    """, (worker_id,))
    reviews = cursor.fetchall()
    conn.close()
    return reviews
