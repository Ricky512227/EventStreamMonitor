"""
WSGI entry point for Notification Service
Used by Gunicorn to serve the application
"""
import sys
import os

# Add parent directory to path for common imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# Import the Flask app from the app module
from app import notification_app

# Gunicorn expects 'application' variable
application = notification_app

if __name__ == "__main__":
    application.run()

