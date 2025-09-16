#!/usr/bin/env python3
"""
Test script to verify webhook verification will work with current configuration
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_webhook_verification():
    """Test the webhook verification logic"""
    print("=== Webhook Verification Test ===\n")
    
    # Get the verify token from environment
    verify_token = os.getenv('WHATSAPP_VERIFY_TOKEN', 'hod_status_verify_token')
    print(f"Environment WHATSAPP_VERIFY_TOKEN: {verify_token}")
    
    # Test with the token Facebook is sending
    facebook_token = "CE_HOD123"
    print(f"Facebook verify token: {facebook_token}")
    
    # Check if they match
    if verify_token == facebook_token:
        print("✅ Tokens match! Webhook verification will succeed.")
    else:
        print("❌ Tokens don't match! Webhook verification will fail.")
        print(f"Expected: {facebook_token}")
        print(f"Got: {verify_token}")
    
    print("\n=== Other Environment Variables ===")
    print(f"WHATSAPP_ACCESS_TOKEN: {os.getenv('WHATSAPP_ACCESS_TOKEN', 'Not set')[:20]}...")
    print(f"WHATSAPP_PHONE_NUMBER_ID: {os.getenv('WHATSAPP_PHONE_NUMBER_ID', 'Not set')}")
    print(f"WEBHOOK_URL: {os.getenv('WEBHOOK_URL', 'Not set')}")

if __name__ == '__main__':
    test_webhook_verification()