"""
Order Model and Helper Functions
Handles job orders between customers and workers, including base amounts and fees.
"""

from models.db import get_db_connection


def create_order(customer_id, worker_id, problem_text, base_amount, fee_amount=0.0):
    """
    Creates a new order record.
    Returns the new order ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO orders (customer_id, worker_id, problem_text, base_amount, fee_amount, status)
        VALUES (?, ?, ?, ?, ?, 'pending')
    """, (customer_id, worker_id, problem_text.strip(), float(base_amount), float(fee_amount)))
    order_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return order_id


def get_order_by_id(order_id):
    """Fetches a single order by ID with customer and worker names."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            o.*,
            c.name AS customer_name,
            c.email AS customer_email,
            w.name AS worker_name,
            w.email AS worker_email,
            wk.skills AS worker_skills
        FROM orders o
        JOIN users c ON o.customer_id = c.id
        JOIN users w ON o.worker_id = w.id
        LEFT JOIN workers wk ON wk.user_id = w.id
        WHERE o.id = ?
    """, (order_id,))
    order = cursor.fetchone()
    conn.close()
    return order


def get_orders_by_customer(customer_id):
    """Fetches all orders placed by a specific customer."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            o.*,
            w.name AS worker_name,
            wk.skills AS worker_skills
        FROM orders o
        JOIN users w ON o.worker_id = w.id
        LEFT JOIN workers wk ON wk.user_id = w.id
        WHERE o.customer_id = ?
        ORDER BY o.id DESC
    """, (customer_id,))
    orders = cursor.fetchall()
    conn.close()
    return orders


def get_orders_by_worker(worker_id):
    """Fetches all orders assigned to a specific worker."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            o.*,
            c.name AS customer_name
        FROM orders o
        JOIN users c ON o.customer_id = c.id
        WHERE o.worker_id = ?
        ORDER BY o.id DESC
    """, (worker_id,))
    orders = cursor.fetchall()
    conn.close()
    return orders


def update_order_status(order_id, status):
    """Updates the status of an existing order."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
    conn.commit()
    conn.close()


def get_revenue_stats():
    """Calculates total base amount, fee revenue, and count of completed orders."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            COUNT(*) AS total_orders,
            COALESCE(SUM(base_amount), 0) AS total_base_revenue,
            COALESCE(SUM(fee_amount), 0) AS total_fee_revenue
        FROM orders
    """)
    stats = cursor.fetchone()
    conn.close()
    return stats


def get_admin_dashboard_data():
    """
    Fetches full financial and operational statistics for the admin dashboard:
    - Total subscription revenue (Monthly @ ₹30, Yearly @ ₹300)
    - Total 5% consulting fee revenue from orders
    - Total combined platform revenue
    - Recent orders and recent subscriptions
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Subscription Revenue Calculation
    cursor.execute("""
        SELECT 
            COUNT(CASE WHEN plan = 'monthly' THEN 1 END) AS monthly_count,
            COUNT(CASE WHEN plan = 'yearly' THEN 1 END) AS yearly_count
        FROM subscriptions
    """)
    sub_counts = cursor.fetchone()
    monthly_subs = sub_counts["monthly_count"] or 0
    yearly_subs = sub_counts["yearly_count"] or 0
    subscription_revenue = (monthly_subs * 30.0) + (yearly_subs * 300.0)

    # 2. Orders & Consulting Fee Revenue
    cursor.execute("""
        SELECT 
            COUNT(*) AS total_orders,
            COALESCE(SUM(base_amount), 0) AS total_base_amount,
            COALESCE(SUM(fee_amount), 0) AS total_fee_revenue
        FROM orders
    """)
    order_stats = cursor.fetchone()
    fee_revenue = float(order_stats["total_fee_revenue"] or 0.0)
    total_orders = order_stats["total_orders"] or 0
    total_base_amount = float(order_stats["total_base_amount"] or 0.0)

    total_platform_revenue = subscription_revenue + fee_revenue

    # 3. Overall System Counts
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'customer'")
    customer_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM workers")
    worker_count = cursor.fetchone()[0]

    # 4. Recent Orders List
    cursor.execute("""
        SELECT 
            o.*,
            c.name AS customer_name,
            c.email AS customer_email,
            w.name AS worker_name,
            wk.skills AS worker_skills
        FROM orders o
        JOIN users c ON o.customer_id = c.id
        JOIN users w ON o.worker_id = w.id
        LEFT JOIN workers wk ON wk.user_id = w.id
        ORDER BY o.id DESC
        LIMIT 15
    """)
    recent_orders = cursor.fetchall()

    # 5. Recent Subscriptions List
    cursor.execute("""
        SELECT 
            s.*,
            u.name AS user_name,
            u.email AS user_email
        FROM subscriptions s
        JOIN users u ON s.user_id = u.id
        ORDER BY s.id DESC
        LIMIT 15
    """)
    recent_subscriptions = cursor.fetchall()

    conn.close()

    return {
        "subscription_revenue": subscription_revenue,
        "monthly_subs_count": monthly_subs,
        "yearly_subs_count": yearly_subs,
        "fee_revenue": fee_revenue,
        "total_platform_revenue": total_platform_revenue,
        "total_orders": total_orders,
        "total_base_amount": total_base_amount,
        "customer_count": customer_count,
        "worker_count": worker_count,
        "recent_orders": recent_orders,
        "recent_subscriptions": recent_subscriptions
    }
