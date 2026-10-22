"""
Unit Tests for Phase 4: Basic Search (Free Users) & Booking
Tests:
- Search by keyword, skill, and city (SQL LIKE without AI)
- Empty results handling
- Haversine distance calculation
- Booking flow with 5% consulting fee for free users
- Booking flow with 0% fee for subscribers
"""

import unittest
from app import app
from services.location import haversine_distance
from models.user import get_user_by_email
from models.worker import get_all_workers
from models.order import get_order_by_id


class TestPhase4BasicSearchAndBooking(unittest.TestCase):
    def setUp(self):
        """Set up test client."""
        self.app = app
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_workers_page_loads(self):
        """Workers page renders all workers by default."""
        res = self.client.get("/workers")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Find Local Skilled Workers", res.data)
        self.assertIn(b"Murugan S", res.data)
        self.assertIn(b"Book Now", res.data)

    def test_filter_by_skill(self):
        """Filter by skill returns matching workers."""
        res = self.client.get("/workers?skill=Electrician")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Karthik Raja", res.data)
        self.assertIn(b"Electrician", res.data)

    def test_filter_by_city(self):
        """Filter by city returns workers in that area."""
        res = self.client.get("/workers?city=Adyar")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Adyar", res.data)

    def test_filter_by_keyword(self):
        """Keyword search finds matches in skills or name."""
        res = self.client.get("/workers?q=pipe")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Plumber", res.data)

    def test_no_results_search(self):
        """Search with no matching workers displays clean empty state."""
        res = self.client.get("/workers?q=nonexistentprofessionxyz")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"No workers found", res.data)
        self.assertIn(b"View All Workers", res.data)

    def test_haversine_distance_calculation(self):
        """Verify Haversine formula distance calculation."""
        # Distance between Adyar (13.0012, 80.2565) and T. Nagar (13.0418, 80.2341) ~ 5.1 km
        dist = haversine_distance(13.0012, 80.2565, 13.0418, 80.2341)
        self.assertIsNotNone(dist)
        self.assertAlmostEqual(dist, 5.1, delta=1.0)

    def test_free_user_booking_incurs_5_percent_fee(self):
        """Free user places an order and incurs 5% consulting fee."""
        # Log in as free user (Arun)
        self.client.post("/login", data={
            "email": "customer.free@example.com",
            "password": "Password123!"
        }, follow_redirects=True)

        worker = get_all_workers()[0]

        # Place booking
        res = self.client.post(f"/book/{worker['user_id']}", data={
            "problem_text": "Water leaking from kitchen faucet",
            "base_amount": "500.0"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # 5% of 500 = 25.0
        self.assertIn(b"25.00", res.data)
        self.assertIn(b"525.00", res.data)

    def test_subscribed_user_booking_has_zero_fee(self):
        """Subscribed user places an order and gets 0% fee."""
        # Log in as subscribed user (Kavitha)
        self.client.post("/login", data={
            "email": "customer.sub@example.com",
            "password": "Password123!"
        }, follow_redirects=True)

        worker = get_all_workers()[0]

        # Place booking
        res = self.client.post(f"/book/{worker['user_id']}", data={
            "problem_text": "Need door hinge tightened",
            "base_amount": "500.0"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # 0% fee
        self.assertIn(b"0.00", res.data)
        self.assertIn(b"Waived for Subscriber", res.data)


if __name__ == "__main__":
    unittest.main()
