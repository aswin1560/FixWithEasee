"""
Unit Tests for Phase 6: Fix It Yourself (DIY Assistant) & Safety Guardrails
Tests:
- Safety filter blocklist (English, Tamil, Hindi)
- Refusal of risky cases (socket sparking, gas smell, geyser not heating)
- Generation of tutorials for safe cases (leaking tap, loose door hinge, clogged sink)
- Presence of tools needed, time needed, stop warning, YouTube links, and find worker button
- Server-side subscription protection
"""

import unittest
from app import app
from services.safety_filter import check_safety_blocklist
from services.diy_tutor import get_diy_tutorial


class TestPhase6FixItYourself(unittest.TestCase):
    def setUp(self):
        """Set up test client."""
        self.app = app
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    # --------------------------------------------------------------------------
    # 1. Safety Blocklist Keyword Tests
    # --------------------------------------------------------------------------
    def test_risky_socket_sparking_refused(self):
        """Electrical socket sparking must be blocked."""
        is_risky, category, warning = check_safety_blocklist("socket sparking")
        self.assertTrue(is_risky)
        self.assertIn("Electrical", category)

    def test_risky_gas_smell_refused(self):
        """Gas smell / LPG leak must be blocked."""
        is_risky, category, warning = check_safety_blocklist("gas smell in kitchen")
        self.assertTrue(is_risky)
        self.assertIn("Gas", category)

    def test_risky_geyser_not_heating_refused(self):
        """Water heater / geyser repair must be blocked."""
        is_risky, category, warning = check_safety_blocklist("geyser not heating")
        self.assertTrue(is_risky)
        self.assertIn("Geyser", category)

    def test_multilingual_safety_blocklist(self):
        """Tamil & Hindi keywords are blocked."""
        # Tamil: current shock
        is_risky1, _, _ = check_safety_blocklist("current shock adikkuthu")
        self.assertTrue(is_risky1)

        # Hindi: bijli ka shock
        is_risky2, _, _ = check_safety_blocklist("bijli ka shock lag raha hai")
        self.assertTrue(is_risky2)

    # --------------------------------------------------------------------------
    # 2. Safe DIY Cases
    # --------------------------------------------------------------------------
    def test_safe_leaking_tap_tutorial(self):
        """Leaking tap generates complete step-by-step tutorial."""
        tut = get_diy_tutorial("leaking tap")
        self.assertFalse(tut["is_risky"])
        self.assertIn("steps", tut)
        self.assertGreaterEqual(len(tut["steps"]), 4)
        self.assertIn("tools_needed", tut)
        self.assertIn("time_needed", tut)
        self.assertIn("stop_warning", tut)
        self.assertIn("youtube_links", tut)
        self.assertGreaterEqual(len(tut["youtube_links"]), 2)

    def test_safe_loose_door_hinge_tutorial(self):
        """Loose door hinge generates complete step-by-step tutorial."""
        tut = get_diy_tutorial("loose door hinge")
        self.assertFalse(tut["is_risky"])
        self.assertIn("steps", tut)
        self.assertIn("tools_needed", tut)
        self.assertIn("stop_warning", tut)

    def test_safe_clogged_sink_tutorial(self):
        """Clogged sink generates complete step-by-step tutorial."""
        tut = get_diy_tutorial("clogged sink")
        self.assertFalse(tut["is_risky"])
        self.assertIn("steps", tut)
        self.assertIn("tools_needed", tut)
        self.assertIn("stop_warning", tut)

    # --------------------------------------------------------------------------
    # 3. HTTP Integration Tests
    # --------------------------------------------------------------------------
    def test_free_user_blocked_from_fix(self):
        """Free user accessing /fix receives 403 Forbidden paywall."""
        self.client.post("/login", data={
            "email": "customer.free@example.com",
            "password": "Password123!"
        }, follow_redirects=True)

        res = self.client.get("/fix")
        self.assertEqual(res.status_code, 403)
        self.assertIn(b"Subscribe to Unlock", res.data)

    def test_subscribed_user_safe_case_view(self):
        """Subscribed user viewing leaking tap receives tutorial and find worker button."""
        self.client.post("/login", data={
            "email": "customer.sub@example.com",
            "password": "Password123!"
        }, follow_redirects=True)

        res = self.client.get("/fix?q=leaking+tap")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Step-by-Step Instructions", res.data)
        self.assertIn(b"Shut Off the Water Supply", res.data)
        self.assertIn(b"Stop and Call a Professional If", res.data)
        self.assertIn(b"Video Help", res.data)
        self.assertIn(b"Still Not Fixed? Find a Worker", res.data)

    def test_subscribed_user_risky_case_view(self):
        """Subscribed user viewing socket sparking receives refusal banner and NO steps."""
        self.client.post("/login", data={
            "email": "customer.sub@example.com",
            "password": "Password123!"
        }, follow_redirects=True)

        res = self.client.get("/fix?q=socket+sparking")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Please Consult a Professional", res.data)
        self.assertIn(b"Electrical Hazards", res.data)
        # MUST NOT contain tutorial instructions
        self.assertNotIn(b"Step-by-Step Instructions", res.data)
        # MUST offer matching professionals
        self.assertIn(b"Find Verified Professionals", res.data)


if __name__ == "__main__":
    unittest.main()
