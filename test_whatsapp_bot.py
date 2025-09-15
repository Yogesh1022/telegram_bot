#!/usr/bin/env python3
"""
Test script for WhatsApp Bot functionality
"""

from app import create_app
from app.whatsapp_service import WhatsAppService

def test_whatsapp_bot():
    """Test WhatsApp bot with proper Flask application context"""
    app = create_app()
    
    with app.app_context():
        print("=== WhatsApp Bot Test ===\n")
        
        # Initialize WhatsApp service
        whatsapp_service = WhatsAppService(
            access_token="test_token",
            phone_number_id="744278420647710",
            verify_token="test_verify_token"
        )
        
        # Test different types of messages
        test_messages = [
            "hod status",
            "is hod available",
            "help",
            "hi",
            "office",
            "random message"
        ]
        
        for message in test_messages:
            print(f"📱 User Message: '{message}'")
            response = whatsapp_service.generate_response(message)
            print(f"🤖 Bot Response:\n{response}\n")
            print("-" * 50)

if __name__ == '__main__':
    test_whatsapp_bot()