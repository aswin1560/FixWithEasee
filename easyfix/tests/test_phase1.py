"""
Unit tests for Phase 1 Setup
Verifies Flask application startup and home page rendering
"""

import unittest
from app import app


class TestPhase1Setup(unittest.TestCase):
    def setUp(self):
        """Set up test client before each test."""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_home_page_loads(self):
        """Test that the home page loads with 200 OK status code."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        # Check for core text and navbar items
        self.assertIn(b"FixWithEase", response.data)
        self.assertIn(b"Find Workers", response.data)
        self.assertIn(b"Fix It Yourself", response.data)
        self.assertIn(b"Pricing", response.data)
        self.assertIn(b"Login", response.data)

    def test_search_box_present(self):
        """Test that the search box exists on the home page."""
        response = self.client.get('/')
        self.assertIn(b'name="q"', response.data)
        self.assertIn(b'Search Workers', response.data)

    def test_pricing_link_present(self):
        """Test that pricing link and banner exist on home page."""
        response = self.client.get('/')
        self.assertIn(b'View Pricing Plans', response.data)
        pricing_response = self.client.get('/pricing')
        self.assertEqual(pricing_response.status_code, 200)
        self.assertIn(b'30', pricing_response.data)
        self.assertIn(b'300', pricing_response.data)


if __name__ == '__main__':
    unittest.main()
