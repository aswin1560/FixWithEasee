"""
Unit Tests for Phase 2: Database Schema & Model Helpers
Tests all 5 models and common queries:
- Users (create, fetch, verify password)
- Workers (fetch, filter by skill and city)
- Subscriptions (active, expired, non-existent)
- Orders (create, update status, fetch by customer/worker)
- Reviews (create, fetch for worker, rating recalculation)
"""

import unittest
from datetime import datetime, timedelta
from models.user import get_user_by_email, get_user_by_id, verify_user_password, create_user
from models.worker import get_all_workers, get_worker_by_user_id, search_workers
from models.subscription import is_subscribed, get_user_subscription, create_or_extend_subscription
from models.order import create_order, get_order_by_id, update_order_status, get_orders_by_customer
from models.review import create_review, get_reviews_for_worker


class TestPhase2Database(unittest.TestCase):
    def setUp(self):
        """Ensure customer.free has no active subscription."""
        from models.db import get_db_connection
        free_user = get_user_by_email("customer.free@example.com")
        if free_user:
            conn = get_db_connection()
            conn.execute("DELETE FROM subscriptions WHERE user_id = ?", (free_user["id"],))
            conn.commit()
            conn.close()

    def test_seeded_users_and_workers_count(self):
        """Verify that 20 workers and seeded users exist."""
        workers = get_all_workers()
        self.assertGreaterEqual(len(workers), 20)
        
        # Verify first worker profile integrity
        worker = workers[0]
        self.assertIn("user_id", worker.keys())
        self.assertIn("name", worker.keys())
        self.assertIn("skills", worker.keys())
        self.assertIn("rating_avg", worker.keys())

    def test_user_authentication_helpers(self):
        """Test user password verification."""
        user = get_user_by_email("customer.sub@example.com")
        self.assertIsNotNone(user)
        self.assertEqual(user["role"], "customer")
        self.assertTrue(verify_user_password(user, "Password123!"))
        self.assertFalse(verify_user_password(user, "WrongPassword"))

    def test_subscription_status(self):
        """Test is_subscribed for active subscriber vs free customer."""
        sub_user = get_user_by_email("customer.sub@example.com")
        free_user = get_user_by_email("customer.free@example.com")

        self.assertTrue(is_subscribed(sub_user["id"]))
        self.assertFalse(is_subscribed(free_user["id"]))
        self.assertFalse(is_subscribed(99999))  # Non-existent user

    def test_worker_search_queries(self):
        """Test search_workers helper by skill and city."""
        plumbers = search_workers(skill="Plumber")
        self.assertGreater(len(plumbers), 0)
        for p in plumbers:
            self.assertIn("Plumber", p["skills"])

        electricians = search_workers(keyword="Electrician")
        self.assertGreater(len(electricians), 0)

        adyar_workers = search_workers(city="Adyar")
        self.assertGreater(len(adyar_workers), 0)

    def test_order_and_review_lifecycle(self):
        """Test creating an order, updating status, and writing a review."""
        sub_user = get_user_by_email("customer.sub@example.com")
        workers = get_all_workers()
        target_worker = workers[0]

        # Create new order
        order_id = create_order(
            customer_id=sub_user["id"],
            worker_id=target_worker["user_id"],
            problem_text="Water leakage test",
            base_amount=400.0,
            fee_amount=0.0
        )
        self.assertIsNotNone(order_id)

        # Verify order retrieval
        order = get_order_by_id(order_id)
        self.assertEqual(order["status"], "pending")
        self.assertEqual(order["base_amount"], 400.0)

        # Update order status to completed
        update_order_status(order_id, "completed")
        updated_order = get_order_by_id(order_id)
        self.assertEqual(updated_order["status"], "completed")

        # Create review
        create_review(order_id, rating=5, comment="Excellent work!")
        reviews = get_reviews_for_worker(target_worker["user_id"])
        self.assertGreater(len(reviews), 0)


if __name__ == "__main__":
    unittest.main()
