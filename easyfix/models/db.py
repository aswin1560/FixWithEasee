"""
Database Connection and Utilities for SQLite
Supports both local execution and Vercel serverless (/tmp writable directory).
Simple and clean SQL queries for easy future migration to MySQL/Postgres.
"""

import os
import shutil
import sqlite3

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGINAL_DB_PATH = os.path.join(BASE_DIR, "database.db")

# Detect Vercel serverless environment
IS_VERCEL = bool(os.environ.get("VERCEL"))

if IS_VERCEL:
    # In Vercel serverless containers, only /tmp is writable
    DB_PATH = os.environ.get("DATABASE_PATH", "/tmp/database.db")
else:
    # Local development or test override
    DB_PATH = os.environ.get("DATABASE_PATH", ORIGINAL_DB_PATH)


def _ensure_database_ready():
    """
    Ensures that the SQLite database file exists and is writable.
    In Vercel serverless environments, copies the pre-seeded database
    into /tmp or auto-seeds if not present.
    """
    if IS_VERCEL and not os.path.exists(DB_PATH):
        # 1. Try copying the pre-seeded database from the project bundle
        if os.path.exists(ORIGINAL_DB_PATH) and os.path.getsize(ORIGINAL_DB_PATH) > 0:
            try:
                os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
                shutil.copy2(ORIGINAL_DB_PATH, DB_PATH)
                return
            except Exception as copy_err:
                print(f"[Vercel] Warning: Could not copy starter database: {copy_err}")

        # 2. If copy is unavailable, dynamically initialize and seed
        try:
            from init_db import init_database
            from seed_db import seed_database
            seed_database()
        except Exception as seed_err:
            print(f"[Vercel] Auto-seed failed: {seed_err}")


def get_db_connection():
    """
    Creates and returns a SQLite database connection with row factory
    enabled so columns can be accessed by name like dictionaries.
    """
    if IS_VERCEL:
        _ensure_database_ready()

    conn = sqlite3.connect(DB_PATH)
    # Enable access to columns by name: row['column_name']
    conn.row_factory = sqlite3.Row
    # Enable foreign key support in SQLite
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
