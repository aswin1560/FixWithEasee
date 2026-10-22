"""
Vercel Serverless Function Entry Point for FixWithEase
Routes all incoming HTTP requests to the Flask application.
"""

import sys
import os

# Add the parent directory (project root) to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import app

# Vercel's Python runtime will find and run this WSGI application
if __name__ == "__main__":
    app.run()
