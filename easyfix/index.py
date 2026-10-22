"""
Root entry point for Vercel and WSGI servers.
Exports the Flask application instance 'app'.
"""

from app import app

# Vercel finds and binds this WSGI application instance
if __name__ == "__main__":
    app.run()
