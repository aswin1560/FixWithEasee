"""
Database Seeding Script
Populates the database with:
- 20 realistic skilled workers located across Chennai neighborhoods
- Sample customer accounts (one subscribed, one free)
- Sample orders and reviews
- Displays row counts for every table to verify setup
"""

import os
from werkzeug.security import generate_password_hash
from init_db import init_database
from models.db import get_db_connection
from models.subscription import create_or_extend_subscription


def seed_database():
    """Initializes tables and populates seed data."""
    # Ensure tables exist
    init_database()

    conn = get_db_connection()
    cursor = conn.cursor()

    # Clear existing data for a clean seed
    cursor.execute("DELETE FROM reviews;")
    cursor.execute("DELETE FROM orders;")
    cursor.execute("DELETE FROM subscriptions;")
    cursor.execute("DELETE FROM workers;")
    cursor.execute("DELETE FROM users;")
    try:
        cursor.execute("DELETE FROM sqlite_sequence;")
    except Exception:
        pass
    conn.commit()

    default_password = generate_password_hash("Password123!")

    # 1. Seed Customer Accounts
    # Subscribed Customer (Kavitha Raman in Adyar)
    cursor.execute("""
        INSERT INTO users (name, email, password_hash, role, city, lat, lng)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ("Kavitha Raman", "customer.sub@example.com", default_password, "customer", "Adyar, Chennai", 13.0012, 80.2565))
    sub_customer_id = cursor.lastrowid

    # Free Customer (Arun Kumar in Anna Nagar)
    cursor.execute("""
        INSERT INTO users (name, email, password_hash, role, city, lat, lng)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ("Arun Kumar", "customer.free@example.com", default_password, "customer", "Anna Nagar, Chennai", 13.0850, 80.2101))
    free_customer_id = cursor.lastrowid

    # Admin Account
    cursor.execute("""
        INSERT INTO users (name, email, password_hash, role, city, lat, lng)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ("Admin Manager", "admin@example.com", default_password, "admin", "Chennai", 13.0827, 80.2707))

    conn.commit()

    # Create active subscription for Kavitha
    create_or_extend_subscription(sub_customer_id, plan="monthly", days=30)

    # 2. 20 Sample Skilled Workers in Chennai
    sample_workers = [
        # Plumbers
        {
            "name": "Murugan S",
            "email": "murugan.plumber@example.com",
            "city": "T. Nagar, Chennai",
            "lat": 13.0418,
            "lng": 80.2341,
            "skills": "Plumber, Pipe Repair, Tap Fixing, Leakage",
            "exp": 8,
            "rating": 4.9,
            "available": 1,
            "verified": 1
        },
        {
            "name": "Senthil Nathan",
            "email": "senthil.plumb@example.com",
            "city": "Velachery, Chennai",
            "lat": 12.9815,
            "lng": 80.2180,
            "skills": "Plumber, Bathroom Fitting, Drainage, Motor Pump",
            "exp": 11,
            "rating": 4.8,
            "available": 1,
            "verified": 1
        },
        {
            "name": "Rajesh Kannan",
            "email": "rajesh.pipe@example.com",
            "city": "Porur, Chennai",
            "lat": 13.0382,
            "lng": 80.1565,
            "skills": "Plumber, Water Tank Cleaning, Tap Fitting",
            "exp": 5,
            "rating": 4.6,
            "available": 1,
            "verified": 1
        },
        {
            "name": "Babu V",
            "email": "babu.plumbing@example.com",
            "city": "Tambaram, Chennai",
            "lat": 12.9249,
            "lng": 80.1000,
            "skills": "Plumber, General Plumbing, Sink Unclogging",
            "exp": 6,
            "rating": 4.5,
            "available": 0,  # Currently busy
            "verified": 1
        },

        # Electricians
        {
            "name": "Karthik Raja",
            "email": "karthik.electric@example.com",
            "city": "Adyar, Chennai",
            "lat": 13.0012,
            "lng": 80.2565,
            "skills": "Electrician, Wiring, Switchboard, Fan Repair, MCB",
            "exp": 9,
            "rating": 4.9,
            "available": 1,
            "verified": 1
        },
        {
            "name": "Vigneshwaran P",
            "email": "vignesh.power@example.com",
            "city": "Mylapore, Chennai",
            "lat": 13.0368,
            "lng": 80.2676,
            "skills": "Electrician, Inverter Setup, Short Circuit, Lighting",
            "exp": 7,
            "rating": 4.7,
            "available": 1,
            "verified": 1
        },
        {
            "name": "Manikandan R",
            "email": "mani.electric@example.com",
            "city": "Anna Nagar, Chennai",
            "lat": 13.0850,
            "lng": 80.2101,
            "skills": "Electrician, Appliance Wiring, Fuse, Ceiling Fan",
            "exp": 12,
            "rating": 4.8,
            "available": 1,
            "verified": 1
        },
        {
            "name": "Dinesh Kumar",
            "email": "dinesh.electric@example.com",
            "city": "Chromepet, Chennai",
            "lat": 12.9516,
            "lng": 80.1462,
            "skills": "Electrician, Power Socket, Earthing, Meter Board",
            "exp": 4,
            "rating": 4.4,
            "available": 1,
            "verified": 1
        },

        # Carpenters
        {
            "name": "Gopalakrishnan M",
            "email": "gopal.wood@example.com",
            "city": "Guindy, Chennai",
            "lat": 13.0067,
            "lng": 80.2026,
            "skills": "Carpenter, Furniture Repair, Door Lock, Hinge Fixing",
            "exp": 14,
            "rating": 4.9,
            "available": 1,
            "verified": 1
        },
        {
            "name": "Anand Mohan",
            "email": "anand.carpenter@example.com",
            "city": "Kodambakkam, Chennai",
            "lat": 13.0519,
            "lng": 80.2255,
            "skills": "Carpenter, Modular Kitchen, Wardrobe Repair, Polishing",
            "exp": 8,
            "rating": 4.7,
            "available": 1,
            "verified": 1
        },
        {
            "name": "Saravanan T",
            "email": "saravanan.wood@example.com",
            "city": "Sholinganallur, Chennai",
            "lat": 12.9010,
            "lng": 80.2279,
            "skills": "Carpenter, Table Assembly, Window Latch, Bed Frame",
            "exp": 5,
            "rating": 4.5,
            "available": 1,
            "verified": 1
        },
        {
            "name": "Ramesh Chander",
            "email": "ramesh.carpentry@example.com",
            "city": "Alwarpet, Chennai",
            "lat": 13.0336,
            "lng": 80.2520,
            "skills": "Carpenter, Antique Furniture, Custom Shelves",
            "exp": 15,
            "rating": 4.9,
            "available": 0,  # Currently busy
            "verified": 1
        },

        # Painters
        {
            "name": "Praveen Kumar",
            "email": "praveen.paint@example.com",
            "city": "Thiruvanmiyur, Chennai",
            "lat": 12.9830,
            "lng": 80.2594,
            "skills": "Painter, Interior Painting, Wall Putty, Waterproofing",
            "exp": 9,
            "rating": 4.8,
            "available": 1,
            "verified": 1
        },
        {
            "name": "Vijay Shankar",
            "email": "vijay.colors@example.com",
            "city": "Nungambakkam, Chennai",
            "lat": 13.0569,
            "lng": 80.2425,
            "skills": "Painter, Exterior Painting, Texture Design, Wood Stain",
            "exp": 6,
            "rating": 4.6,
            "available": 1,
            "verified": 1
        },
        {
            "name": "Kishore Babu",
            "email": "kishore.paint@example.com",
            "city": "Royapettah, Chennai",
            "lat": 13.0583,
            "lng": 80.2642,
            "skills": "Painter, Touchup Painting, Damp Proofing, Stencil",
            "exp": 7,
            "rating": 4.5,
            "available": 1,
            "verified": 1
        },

        # AC & Appliance Repair
        {
            "name": "Syed Imran",
            "email": "syed.ac@example.com",
            "city": "Kilpauk, Chennai",
            "lat": 13.0826,
            "lng": 80.2407,
            "skills": "AC Repair, Air Conditioner Service, Gas Refill, Cooling",
            "exp": 10,
            "rating": 4.9,
            "available": 1,
            "verified": 1
        },
        {
            "name": "Selvam G",
            "email": "selvam.cooling@example.com",
            "city": "Pallavaram, Chennai",
            "lat": 12.9675,
            "lng": 80.1491,
            "skills": "AC Repair, Split AC Installation, Coil Cleaning",
            "exp": 8,
            "rating": 4.7,
            "available": 1,
            "verified": 1
        },
        {
            "name": "Ravi Teja",
            "email": "ravi.appliances@example.com",
            "city": "Perambur, Chennai",
            "lat": 13.1075,
            "lng": 80.2434,
            "skills": "Appliance Repair, Washing Machine, Refrigerator, Microwave",
            "exp": 11,
            "rating": 4.8,
            "available": 1,
            "verified": 1
        },
        {
            "name": "Mohamed Farook",
            "email": "farook.appliances@example.com",
            "city": "Egmore, Chennai",
            "lat": 13.0732,
            "lng": 80.2609,
            "skills": "Appliance Repair, Water Purifier, Geyser Repair, Mixer Grinder",
            "exp": 7,
            "rating": 4.6,
            "available": 1,
            "verified": 1
        },
        {
            "name": "Deepak Balaji",
            "email": "deepak.handyman@example.com",
            "city": "Besant Nagar, Chennai",
            "lat": 13.0003,
            "lng": 80.2667,
            "skills": "Plumber, Carpenter, Handyman, General Fixes",
            "exp": 6,
            "rating": 4.7,
            "available": 1,
            "verified": 1
        }
    ]

    first_worker_id = None
    for w in sample_workers:
        cursor.execute("""
            INSERT INTO users (name, email, password_hash, role, city, lat, lng)
            VALUES (?, ?, ?, 'worker', ?, ?, ?)
        """, (w["name"], w["email"], default_password, w["city"], w["lat"], w["lng"]))
        worker_user_id = cursor.lastrowid
        if first_worker_id is None:
            first_worker_id = worker_user_id

        cursor.execute("""
            INSERT INTO workers (user_id, skills, experience_years, rating_avg, is_available, verified)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (worker_user_id, w["skills"], w["exp"], w["rating"], w["available"], w["verified"]))

    conn.commit()

    # 3. Seed Sample Completed Order & Review
    # Order placed by Kavitha with Murugan (first worker)
    cursor.execute("""
        INSERT INTO orders (customer_id, worker_id, problem_text, base_amount, fee_amount, status)
        VALUES (?, ?, 'Fixing leaky kitchen sink pipe', 350.0, 0.0, 'completed')
    """, (sub_customer_id, first_worker_id))
    order_id = cursor.lastrowid

    # Review for the completed order
    cursor.execute("""
        INSERT INTO reviews (order_id, rating, comment)
        VALUES (?, 5, 'Quick response, fixed the pipe in 20 minutes without mess. Very polite!')
    """, (order_id,))

    conn.commit()

    # 4. Print Table Row Counts to confirm
    tables = ["users", "workers", "subscriptions", "orders", "reviews"]
    print("\n================ DATABASE SEED REPORT ================")
    for tbl in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {tbl}")
        count = cursor.fetchone()[0]
        print(f"Table '{tbl}': {count} rows")
    print("======================================================\n")

    conn.close()


if __name__ == "__main__":
    seed_database()
