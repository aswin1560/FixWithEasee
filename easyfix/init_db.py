"""
Database Initialization Script
Creates all required tables for AI-Powered Local Skill Connect:
- users
- workers
- subscriptions
- orders
- reviews
"""

import sqlite3
import os
from models.db import DB_PATH, get_db_connection


def init_database():
    """Initializes the SQLite database with all needed tables."""
    print(f"Initializing database at: {DB_PATH}")
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('customer', 'worker', 'admin')),
        city TEXT NOT NULL,
        lat REAL,
        lng REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. workers table (linked to users via user_id)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS workers (
        user_id INTEGER PRIMARY KEY,
        skills TEXT NOT NULL,
        experience_years INTEGER NOT NULL DEFAULT 1,
        rating_avg REAL NOT NULL DEFAULT 5.0,
        is_available INTEGER NOT NULL DEFAULT 1 CHECK(is_available IN (0, 1)),
        verified INTEGER NOT NULL DEFAULT 1 CHECK(verified IN (0, 1)),
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    # 3. subscriptions table (for customer subscription status)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        plan TEXT NOT NULL CHECK(plan IN ('monthly', 'yearly')),
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'expired', 'cancelled')),
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    # 4. orders table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        worker_id INTEGER NOT NULL,
        problem_text TEXT NOT NULL,
        base_amount REAL NOT NULL,
        fee_amount REAL NOT NULL DEFAULT 0.0,
        status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'accepted', 'in_progress', 'completed', 'cancelled')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES users (id),
        FOREIGN KEY (worker_id) REFERENCES users (id)
    );
    """)

    # 5. reviews table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER UNIQUE NOT NULL,
        rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
        comment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    conn.close()
    print("Database tables initialized successfully!")


if __name__ == "__main__":
    init_database()
