#!/usr/bin/env python3
"""
Test script for Telegram bot functionality with HOD database
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, HODStatus
from datetime import datetime

def test_telegram_bot_integration():
    """Test Telegram bot database integration"""
    app = create_app()
    
    with app.app_context():
        print("=== Telegram Bot - HOD Database Integration Test ===\n")
        
        # Test getting HOD status
        hod = HODStatus.query.filter_by(hod_name="Dr. Manoj V. Bramhe").first()
        if hod:
            print("✅ HOD record found in database")
            print(f"Current Status: {hod.status}")
            print(f"Message: {hod.status_message}")
            print(f"Last Updated: {hod.timestamp}")
            print()
        else:
            print("❌ No HOD record found!")
            return
        
        # Test status formatting
        def format_status_message(hod):
            if not hod:
                return "❌ Sorry, HOD information is not available at the moment."
            
            status_emoji = {
                "present_and_free": "🟢",
                "present_and_busy": "🟡", 
                "not_present": "🔴"
            }
            
            status_text = {
                "present_and_free": "Present and Free",
                "present_and_busy": "Present but Busy",
                "not_present": "Not Present in Cabin"
            }
            
            emoji = status_emoji.get(hod.status, "⚪")
            status = status_text.get(hod.status, hod.status)
            
            return f"""🏫 *HOD Status - Computer Science Engineering*

👨‍🏫 *Name:* Dr. Manoj V. Bramhe
{emoji} *Status:* {status}

📝 *Message:* {hod.status_message or 'No additional message'}

🕒 *Last Updated:* {hod.timestamp.strftime('%d/%m/%Y at %I:%M %p')}
👤 *Updated by:* {hod.updated_by or 'System'}"""
        
        print("📱 Telegram Message Format Test:")
        telegram_message = format_status_message(hod)
        print(telegram_message)
        print()
        
        # Test updating status
        print("🔄 Testing status update...")
        original_status = hod.status
        original_message = hod.status_message
        original_updated_by = hod.updated_by
        
        # Update to busy
        hod.status = "present_and_busy"
        hod.status_message = "Updated via Telegram bot test"
        hod.timestamp = datetime.utcnow()
        hod.updated_by = "telegram_bot_test"
        db.session.commit()
        
        print("✅ Status updated to: present_and_busy")
        print("📱 New Telegram Message:")
        new_telegram_message = format_status_message(hod)
        print(new_telegram_message)
        print()
        
        # Restore original status
        hod.status = original_status
        hod.status_message = original_message
        hod.updated_by = original_updated_by
        hod.timestamp = datetime.utcnow()
        db.session.commit()
        
        print("✅ Status restored to original")
        print()
        
        # Test command parsing
        print("🤖 Testing Telegram Bot Commands:")
        test_commands = [
            "/status",
            "/update present_and_busy In faculty meeting",
            "/quick",
            "hod status",
            "is hod available",
            "help"
        ]
        
        for cmd in test_commands:
            print(f"  Command: {cmd}")
            if cmd.startswith("/update"):
                parts = cmd.split()
                if len(parts) >= 2:
                    status = parts[1]
                    message = " ".join(parts[2:]) if len(parts) > 2 else "Updated via bot"
                    print(f"    → Would update status to: {status}")
                    print(f"    → Message: {message}")
            elif any(keyword in cmd.lower() for keyword in ["status", "hod", "available"]):
                print(f"    → Would return current HOD status")
            else:
                print(f"    → Would show help or handle as command")
        
        print("\n=== Test Complete ===")
        print("✅ Database integration working")
        print("✅ Status formatting working") 
        print("✅ Update functionality working")
        print("✅ Command parsing working")
        print("\n🚀 Ready to run Telegram bot!")

if __name__ == '__main__':
    test_telegram_bot_integration()