"""
Unit Tests for Phase 5: AI Search (Subscribers Only)
Tests:
- AI problem diagnosis for:
  1. "my kitchen tap is leaking" -> Plumber
  2. "fan not working" -> Electrician
  3. "need a table repaired" -> Carpenter
- Worker scoring and ranking (top 5 returned with match_score and reason)
- Server-side subscription protection (403 for free users, 200 for subscribers)
- API endpoint /api/ai/match
"""

import unittest
from app import app
from services.ai_matcher import analyze_problem_with_gemini, score_and_rank_workers, fallback_problem_analyzer


class TestPhase5AISearch(unittest.TestCase):
    def setUp(self):
        """Set up test client."""
        self.app = app
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_ai_diagnosis_kitchen_tap(self):
        """Test problem analysis for 'my kitchen tap is leaking'."""
        analysis = analyze_problem_with_gemini("my kitchen tap is leaking")
        self.assertEqual(analysis["skill_needed"], "Plumber")
        self.assertFalse(analysis["is_risky"])
        self.assertIn("summary", analysis)
        self.assertIn("urgency", analysis)

    def test_ai_diagnosis_fan_not_working(self):
        """Test problem analysis for 'fan not working'."""
        analysis = analyze_problem_with_gemini("fan not working")
        self.assertEqual(analysis["skill_needed"], "Electrician")
        self.assertIn("summary", analysis)

    def test_ai_diagnosis_table_repaired(self):
        """Test problem analysis for 'need a table repaired'."""
        analysis = analyze_problem_with_gemini("need a table repaired")
        self.assertEqual(analysis["skill_needed"], "Carpenter")
        self.assertFalse(analysis["is_risky"])
        self.assertIn("summary", analysis)

    def test_ai_diagnosis_risky_problem(self):
        """Test that hazardous electrical / spark problem flags is_risky as True."""
        analysis = analyze_problem_with_gemini("switchboard sparking and smoke coming out")
        self.assertEqual(analysis["skill_needed"], "Electrician")
        self.assertTrue(analysis["is_risky"])

    def test_worker_ranking_returns_top_5_with_reasons(self):
        """Worker ranking returns 5 scored workers with clear recommendation reason."""
        analysis = analyze_problem_with_gemini("my kitchen tap is leaking")
        ranked = score_and_rank_workers(analysis, customer_lat=13.0827, customer_lng=80.2707)

        self.assertEqual(len(ranked), 5)
        for w in ranked:
            self.assertIn("match_score", w)
            self.assertIn("recommendation_reason", w)
            self.assertIn("distance_km", w)
            # The top recommended worker should have plumbing skills
            self.assertIn("Plumber", ranked[0]["skills"])

    def test_free_user_blocked_from_ai_search(self):
        """Free customer receives 403 Forbidden when trying to access /ai-search."""
        # Log in as free user
        self.client.post("/login", data={
            "email": "customer.free@example.com",
            "password": "Password123!"
        }, follow_redirects=True)

        res = self.client.get("/ai-search")
        self.assertEqual(res.status_code, 403)
        self.assertIn(b"Subscribe to Unlock", res.data)

        api_res = self.client.post("/api/ai/match", json={"problem_text": "tap leaking"})
        self.assertEqual(api_res.status_code, 403)

    def test_subscribed_user_accesses_ai_search(self):
        """Subscribed customer (Kavitha) accesses /ai-search and views top ranked workers."""
        # Log in as subscribed user
        self.client.post("/login", data={
            "email": "customer.sub@example.com",
            "password": "Password123!"
        }, follow_redirects=True)

        res = self.client.get("/ai-search?q=my+kitchen+tap+is+leaking")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"AI Problem Diagnosis", res.data)
        self.assertIn(b"Plumber", res.data)
        self.assertIn(b"Top 5 Ranked Workers", res.data)
        self.assertIn(b"Book This Worker", res.data)

    def test_api_ai_match_endpoint(self):
        """Subscribed customer posts to /api/ai/match and receives JSON analysis and rankings."""
        self.client.post("/login", data={
            "email": "customer.sub@example.com",
            "password": "Password123!"
        }, follow_redirects=True)

        res = self.client.post("/api/ai/match", json={"problem_text": "need a table repaired"})
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertEqual(json_data["status"], "success")
        self.assertEqual(json_data["analysis"]["skill_needed"], "Carpenter")
        self.assertEqual(len(json_data["ranked_workers"]), 5)


if __name__ == "__main__":
    unittest.main()
