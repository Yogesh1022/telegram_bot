#!/usr/bin/env python3
"""
Windows-compatible deployment script using waitress WSGI server.
This replaces gunicorn which doesn't work on Windows due to fcntl dependency.
"""

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

from app import create_app
from waitress import serve

# Create Flask application instance
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"Starting waitress server on {host}:{port}")
    print("Press Ctrl+C to stop the server")
    
    # Use waitress to serve the Flask app
    serve(app, host=host, port=port, threads=6)