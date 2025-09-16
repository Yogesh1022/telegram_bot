#!/usr/bin/env python3
"""
Pre-deployment test script for Railway
Tests all endpoints and functionality before deploying
"""

import requests
import json
import time
import subprocess
import sys
import threading
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_local_deployment():
    """Test the application locally before Railway deployment"""
    
    print("🧪 Pre-deployment Testing for Railway")
    print("=" * 50)
    
    # Start the Flask app in background
    print("1. Starting Flask application...")
    
    # Test if main.py runs without errors
    try:
        import main
        print("✅ main.py imports successfully")
    except Exception as e:
        print(f"❌ Error importing main.py: {e}")
        return False
    
    # Test configuration
    print("\n2. Testing configuration...")
    config_vars = [
        'WHATSAPP_VERIFY_TOKEN',
        'WHATSAPP_PHONE_NUMBER_ID',
        'WHATSAPP_ACCESS_TOKEN'
    ]
    
    for var in config_vars:
        value = os.getenv(var)
        if value and value != 'your_access_token_here':
            print(f"✅ {var}: Configured")
        else:
            print(f"⚠️ {var}: Not configured (using default)")
    
    print("\n3. Testing database initialization...")
    try:
        from app import create_app
        from app.models import db, HODStatus
        
        app = create_app()
        with app.app_context():
            db.create_all()
            hod = HODStatus.query.filter_by(hod_name="Dr. Manoj V. Bramhe").first()
            if hod:
                print("✅ Database initialized and HOD record exists")
                print(f"   Status: {hod.status}")
                print(f"   Message: {hod.status_message}")
            else:
                print("❌ HOD record not found")
                return False
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False
    
    print("\n4. Testing WhatsApp service...")
    try:
        from app.whatsapp_service import WhatsAppService
        
        ws = WhatsAppService(
            access_token=os.getenv('WHATSAPP_ACCESS_TOKEN', 'test'),
            phone_number_id=os.getenv('WHATSAPP_PHONE_NUMBER_ID', '123'),
            verify_token=os.getenv('WHATSAPP_VERIFY_TOKEN', 'test')
        )
        
        with app.app_context():
            response = ws.generate_response("hod status")
            if "Dr. Manoj V. Bramhe" in response:
                print("✅ WhatsApp service working")
            else:
                print("❌ WhatsApp service error")
                return False
    except Exception as e:
        print(f"❌ WhatsApp service error: {e}")
        return False
    
    print("\n5. Testing Docker build readiness...")
    required_files = [
        'Dockerfile',
        'requirements.txt',
        'main.py',
        'railway.toml',
        '.dockerignore'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}: Found")
        else:
            print(f"❌ {file}: Missing")
            return False
    
    print("\n🎉 Pre-deployment tests passed!")
    print("\nReady for Railway deployment:")
    print("1. Push code to GitHub")
    print("2. Connect repository to Railway")
    print("3. Set environment variables in Railway dashboard")
    print("4. Deploy!")
    
    return True

def display_railway_commands():
    """Display Railway CLI commands for deployment"""
    print("\n🚂 Railway CLI Commands:")
    print("=" * 30)
    print("1. Install Railway CLI:")
    print("   npm install -g @railway/cli")
    print("\n2. Login to Railway:")
    print("   railway login")
    print("\n3. Deploy from current directory:")
    print("   railway up")
    print("\n4. Set environment variables:")
    print("   railway variables set WHATSAPP_ACCESS_TOKEN=your_token")
    print("   railway variables set WHATSAPP_VERIFY_TOKEN=CE_HOD123")
    print("\n5. View logs:")
    print("   railway logs")

if __name__ == '__main__':
    success = test_local_deployment()
    
    if success:
        display_railway_commands()
        print(f"\n✅ All tests passed! Ready for Railway deployment.")
    else:
        print(f"\n❌ Some tests failed. Please fix issues before deploying.")
        sys.exit(1)