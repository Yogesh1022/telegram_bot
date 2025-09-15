#!/usr/bin/env python3
"""
Main application entry point for the HOD Status Tracking Flask App.
"""

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

from app import create_app

# Create Flask application instance using the factory pattern
app = create_app()

# Primary route - returns HTML heading for root URL (for backward compatibility)
@app.route('/health')
def health():
    return '<h1>Flask Server is Live</h1>'

# Execution block - runs the web server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)