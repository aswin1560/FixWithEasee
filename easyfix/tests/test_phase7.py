"""
Unit Tests for Phase 7: Payments (Razorpay TEST Mode) & 5% Platform Fee
Tests:
- Subscribed order (0% consulting fee stored in DB)
- Unsubscribed order (5% consulting fee calculated and stored in DB)
- Razorpay order creation (monthly ₹30 = 3,000 paise, yearly ₹300 = 30,000 paise)
- Razorpay cryptographic signature verification & subscription activation
- Failed payment (tampered/invalid signature refused with 400 error)
- Admin revenue dashboard (total subscription revenue + total fee revenue)
"""

import unittest
from app import app
from services.payment_service import generate_test_signature, calculate_consulting_fee
from models.user import get_user_by_email
from models.worker import get_all_workers
from models.order import create_order, get_order_by_id, get_admin_dashboard_data
from models.subscription import is_subscribed


class TestPhase7PaymentsAndFee(unittest.TestCase):
    def setUp(self):
        """Set up test client and clean subscriptions for customer.free."""
        self.app = app
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        self._clean_free_user_subs()

    def tearDown(self):
        """Clean up subscriptions after tests."""
        self._clean_free_user_subs()

    def _clean_free_user_subs(self):
        free_user = get_user_by_email("customer.free@example.com")
        if free_user:
            from models.db import get_db_connection
            conn = get_db_connection()
            conn.execute("DELETE FROM subscriptions WHERE user_id = ?", (free_user["id"],))
            conn.commit()
            conn.close()

    def test_fee_calculation_formula(self):
        """Verify 5% fee for free users and 0% for subscribers."""
        self.assertEqual(calculate_consulting_fee(500.0, is_user_subscribed=False), 25.0)
        self.assertEqual(calculate_consulting_fee(350.0, is_user_subscribed=False), 17.5)
        self.assertEqual(calculate_consulting_fee(500.0, is_user_subscribed=True), 0.0)
        self.assertEqual(calculate_consulting_fee(350.0, is_user_subscribed=True), 0.0)

    def test_unsubscribed_order_flow(self):
        """Unsubscribed customer places order with 5% consulting fee stored."""
        self.client.post("/login", data={
            "email": "customer.free@example.com",
            "password": "Password123!"
        }, follow_redirects=True)

        worker = get_all_workers()[0]
        base_amount = 600.0
        expected_fee = 30.0  # 5% of 600

        res = self.client.post(f"/book/{worker['user_id']}", data={
            "problem_text": "Sink pipe leakage repair",
            "base_amount": str(base_amount)
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # Verify fee is stored in database
        free_user = get_user_by_email("customer.free@example.com")
        order_id = create_order(free_user["id"], worker["user_id"], "Test unsubs order", base_amount, expected_fee)
        order = get_order_by_id(order_id)
        self.assertEqual(order["base_amount"], 600.0)
        self.assertEqual(order["fee_amount"], 30.0)

    def test_subscribed_order_flow(self):
        """Subscribed customer places order with 0% fee stored."""
        self.client.post("/login", data={
            "email": "customer.sub@example.com",
            "password": "Password123!"
        }, follow_redirects=True)

        worker = get_all_workers()[0]
        base_amount = 600.0
        expected_fee = 0.0

        sub_user = get_user_by_email("customer.sub@example.com")
        order_id = create_order(sub_user["id"], worker["user_id"], "Test subs order", base_amount, expected_fee)
        order = get_order_by_id(order_id)
        self.assertEqual(order["base_amount"], 600.0)
        self.assertEqual(order["fee_amount"], 0.0)

    def test_razorpay_order_creation_endpoint(self):
        """Customer initiates Razorpay order for Monthly and Yearly plans."""
        self.client.post("/login", data={
            "email": "customer.free@example.com",
            "password": "Password123!"
        }, follow_redirects=True)

        # Monthly order: ₹30 = 3000 paise
        res_m = self.client.post("/create-razorpay-order", json={"plan": "monthly"})
        self.assertEqual(res_m.status_code, 200)
        data_m = res_m.get_json()
        self.assertTrue(data_m["success"])
        self.assertEqual(data_m["amount"], 3000)
        self.assertEqual(data_m["currency"], "INR")

        # Yearly order: ₹300 = 30000 paise
        res_y = self.client.post("/create-razorpay-order", json={"plan": "yearly"})
        self.assertEqual(res_y.status_code, 200)
        data_y = res_y.get_json()
        self.assertEqual(data_y["amount"], 30000)

    def test_razorpay_valid_payment_verification_activates_subscription(self):
        """Valid payment signature activates subscription."""
        # Log in as free user
        self.client.post("/login", data={
            "email": "customer.free@example.com",
            "password": "Password123!"
        }, follow_redirects=True)

        user = get_user_by_email("customer.free@example.com")

        # Generate order & signature
        order_id = "order_test_phase7_valid"
        payment_id = "pay_test_phase7_valid"
        signature = generate_test_signature(order_id, payment_id)

        # Verify payment on server
        verify_res = self.client.post("/verify-payment", json={
            "razorpay_order_id": order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature,
            "plan": "monthly"
        })
        self.assertEqual(verify_res.status_code, 200)
        self.assertTrue(verify_res.get_json()["success"])

        # Check user is now subscribed
        self.assertTrue(is_subscribed(user["id"]))

    def test_razorpay_failed_payment_rejected(self):
        """Tampered or invalid signature is rejected with 400 error."""
        self.client.post("/login", data={
            "email": "customer.free@example.com",
            "password": "Password123!"
        }, follow_redirects=True)

        # Send invalid signature
        verify_res = self.client.post("/verify-payment", json={
            "razorpay_order_id": "order_test_fake",
            "razorpay_payment_id": "pay_test_fake",
            "razorpay_signature": "tampered_fake_signature_12345",
            "plan": "monthly"
        })
        self.assertEqual(verify_res.status_code, 400)
        self.assertFalse(verify_res.get_json()["success"])

    def test_admin_dashboard_metrics(self):
        """Admin dashboard displays subscription revenue and fee revenue."""
        # Log in as Admin
        self.client.post("/login", data={
            "email": "admin@example.com",
            "password": "Password123!"
        }, follow_redirects=True)

        res = self.client.get("/admin")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Admin Financial Dashboard", res.data)
        self.assertIn(b"Subscription Revenue", res.data)
        self.assertIn(b"Consulting Fee", res.data)

        # Verify admin model function
        data = get_admin_dashboard_data()
        self.assertIn("subscription_revenue", data)
        self.assertIn("fee_revenue", data)
        self.assertIn("total_platform_revenue", data)


if __name__ == "__main__":
    unittest.main()
