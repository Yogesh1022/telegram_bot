#!/usr/bin/env python3
"""
Combined application runner for HOD Status System
Runs both Flask API server and Telegram bot
"""

import os
import sys
import threading
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_flask_app():
    """Run the Flask application"""
    from app import create_app
    
    app = create_app()
    
    port = int(os.environ.get('PORT', 5001))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    print(f"🌐 Starting Flask API server on {host}:{port}")
    app.run(host=host, port=port, debug=debug, use_reloader=False)

def run_telegram_bot():
    """Run the Telegram bot"""
    print("🤖 Starting Telegram bot...")
    
    # Import and run telegram bot
    import telegrambot
    telegrambot.main()

def main():
    """Main function to run both services"""
    print("🚀 Starting HOD Status System...")
    print("=" * 50)
    
    # Check if Telegram token is provided
    telegram_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not telegram_token:
        print("⚠️  No Telegram token found. Only starting Flask API.")
        run_flask_app()
        return
    
    # Start Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask_app, daemon=True)
    flask_thread.start()
    
    # Give Flask a moment to start
    time.sleep(2)
    
    # Start Telegram bot in main thread
    try:
        run_telegram_bot()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        sys.exit(0)

if __name__ == '__main__':
    main()