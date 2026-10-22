"""
Unit Tests for Phase 8: Polish, Reviews, and Ratings
Tests:
- Order completion lifecycle
- Customer rating and review submission
- Automatic recalculation of worker's average rating
- My Orders listing
- Mobile responsiveness markup
"""

import unittest
from app import app
from models.user import get_user_by_email
from models.worker import get_all_workers, get_worker_by_user_id
from models.order import create_order, get_order_by_id
from models.review import get_review_by_order_id, get_reviews_for_worker


class TestPhase8PolishAndReviews(unittest.TestCase):
    def setUp(self):
        """Set up test client."""
        self.app = app
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_complete_order_and_submit_review(self):
        """Customer marks order completed and leaves 5-star review, updating worker rating."""
        # Log in as subscribed customer
        self.client.post("/login", data={
            "email": "customer.sub@example.com",
            "password": "Password123!"
        }, follow_redirects=True)

        user = get_user_by_email("customer.sub@example.com")
        worker = get_all_workers()[0]
        worker_id = worker["user_id"]

        # 1. Create a test order
        order_id = create_order(
            customer_id=user["id"],
            worker_id=worker_id,
            problem_text="Test pipe fix for review",
            base_amount=400.0,
            fee_amount=0.0
        )

        # 2. Mark order completed
        comp_res = self.client.post(f"/orders/{order_id}/complete", follow_redirects=True)
        self.assertEqual(comp_res.status_code, 200)
        order = get_order_by_id(order_id)
        self.assertEqual(order["status"], "completed")

        # 3. Submit 5-star review
        review_res = self.client.post(f"/orders/{order_id}/review", data={
            "rating": "5",
            "comment": "Punctual, professional, and solved the leak cleanly!"
        }, follow_redirects=True)
        self.assertEqual(review_res.status_code, 200)

        # 4. Verify review is saved
        review = get_review_by_order_id(order_id)
        self.assertIsNotNone(review)
        self.assertEqual(review["rating"], 5)
        self.assertIn("Punctual", review["comment"])

        # 5. Verify worker average rating exists and is updated
        updated_worker = get_worker_by_user_id(worker_id)
        self.assertGreaterEqual(updated_worker["rating_avg"], 4.0)

    def test_my_orders_page_loads(self):
        """Customer can view their bookings on /my-orders."""
        self.client.post("/login", data={
            "email": "customer.sub@example.com",
            "password": "Password123!"
        }, follow_redirects=True)

        res = self.client.get("/my-orders")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"My Orders & Bookings", res.data)

    def test_mobile_responsive_elements(self):
        """Home page includes mobile viewport meta and responsive styles."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'name="viewport"', res.data)
        self.assertIn(b'navToggle', res.data)


if __name__ == "__main__":
    unittest.main()
