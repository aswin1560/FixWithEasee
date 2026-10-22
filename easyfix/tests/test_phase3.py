"""
Unit Tests for Phase 3: Login and Subscription
Tests:
- Subscribed users (HTTP 200 on protected AI routes)
- Never-subscribed users (HTTP 403 on protected AI routes)
- Expired subscription users (HTTP 403 on protected AI routes)
- Unauthenticated users (Redirect to login)
- User registration and login flow
- Mock subscription activation
"""

import unittest
from datetime import datetime, timedelta
from app import app
from models.db import get_db_connection
from models.user import get_user_by_email, create_user
from models.subscription import is_subscribed


class TestPhase3LoginAndSubscription(unittest.TestCase):
    def setUp(self):
        """Set up Flask test client and ensure test database records."""
        self.app = app
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

        # Ensure customer.free has no active subscriptions
        free_user = get_user_by_email("customer.free@example.com")
        if free_user:
            conn = get_db_connection()
            conn.execute("DELETE FROM subscriptions WHERE user_id = ?", (free_user["id"],))
            conn.commit()
            conn.close()

    def test_1_subscribed_user_can_access_ai_routes(self):
        """Subscribed user (Kavitha) can access protected AI routes."""
        login_res = self.client.post("/login", data={
            "email": "customer.sub@example.com",
            "password": "Password123!"
        }, follow_redirects=True)
        self.assertEqual(login_res.status_code, 200)

        # Access /fix page
        fix_res = self.client.get("/fix")
        self.assertEqual(fix_res.status_code, 200)
        self.assertIn(b"Fix It Yourself", fix_res.data)

        # Access /api/ai/match
        api_res = self.client.post("/api/ai/match")
        self.assertEqual(api_res.status_code, 200)
        self.assertIn(b"success", api_res.data)

    def test_2_never_subscribed_user_receives_403(self):
        """Never-subscribed user (Arun) receives 403 on protected AI routes."""
        self.client.post("/login", data={
            "email": "customer.free@example.com",
            "password": "Password123!"
        }, follow_redirects=True)

        # Access /fix page -> must return 403 Forbidden
        fix_res = self.client.get("/fix")
        self.assertEqual(fix_res.status_code, 403)
        self.assertIn(b"Subscribe to Unlock", fix_res.data)

        # Access /api/ai/match -> must return 403 JSON
        api_res = self.client.post("/api/ai/match")
        self.assertEqual(api_res.status_code, 403)
        self.assertIn(b"Subscription Required", api_res.data)

    def test_3_expired_subscription_user_receives_403(self):
        """User whose subscription has passed end_date receives 403."""
        expired_email = "test.expired@example.com"
        user = get_user_by_email(expired_email)
        if not user:
            user_id = create_user(
                name="Expired User",
                email=expired_email,
                password="Password123!",
                role="customer",
                city="Chennai"
            )
        else:
            user_id = user["id"]

        # Insert an expired subscription (ended 5 days ago)
        conn = get_db_connection()
        conn.execute("DELETE FROM subscriptions WHERE user_id = ?", (user_id,))
        past_start = (datetime.now() - timedelta(days=35)).isoformat()
        past_end = (datetime.now() - timedelta(days=5)).isoformat()
        conn.execute("""
            INSERT INTO subscriptions (user_id, plan, start_date, end_date, status)
            VALUES (?, 'monthly', ?, ?, 'active')
        """, (user_id, past_start, past_end))
        conn.commit()
        conn.close()

        # Check server helper returns False
        self.assertFalse(is_subscribed(user_id))

        # Log in as expired user
        self.client.post("/login", data={
            "email": expired_email,
            "password": "Password123!"
        }, follow_redirects=True)

        # Access /fix -> 403
        fix_res = self.client.get("/fix")
        self.assertEqual(fix_res.status_code, 403)

        # Access /api/ai/match -> 403
        api_res = self.client.post("/api/ai/match")
        self.assertEqual(api_res.status_code, 403)

    def test_4_unauthenticated_user_redirected(self):
        """Unauthenticated user accessing protected route is redirected to login."""
        res = self.client.get("/fix")
        self.assertEqual(res.status_code, 302)
        self.assertIn("/login", res.headers.get("Location", ""))

    def test_5_mock_subscribe_activates_subscription(self):
        """Free user clicking mock subscribe unlocks active subscription."""
        # Log in as free user
        self.client.post("/login", data={
            "email": "customer.free@example.com",
            "password": "Password123!"
        }, follow_redirects=True)

        # Initially cannot access /fix -> 403
        self.assertEqual(self.client.get("/fix").status_code, 403)

        # Post mock subscribe to monthly plan
        sub_res = self.client.post("/subscribe", data={"plan": "monthly"}, follow_redirects=True)
        self.assertEqual(sub_res.status_code, 200)

        # User should now be able to access /fix with 200 OK
        fix_res = self.client.get("/fix")
        self.assertEqual(fix_res.status_code, 200)

    def test_6_user_registration_customer_and_worker(self):
        """Test registration flow for both customer and worker."""
        # Register customer
        customer_email = f"cust_{int(datetime.now().timestamp())}@example.com"
        res1 = self.client.post("/register", data={
            "name": "New Customer",
            "email": customer_email,
            "password": "Password123!",
            "role": "customer",
            "city": "Chennai"
        }, follow_redirects=True)
        self.assertEqual(res1.status_code, 200)
        self.assertIn(b"Welcome to FixWithEase", res1.data)

        # Register worker
        worker_email = f"work_{int(datetime.now().timestamp())}@example.com"
        res2 = self.client.post("/register", data={
            "name": "New Worker",
            "email": worker_email,
            "password": "Password123!",
            "role": "worker",
            "city": "Chennai",
            "skills": "Plumber, Pipe Repair",
            "experience_years": "5"
        }, follow_redirects=True)
        self.assertEqual(res2.status_code, 200)
        self.assertIn(b"Welcome to FixWithEase", res2.data)


if __name__ == "__main__":
    unittest.main()
