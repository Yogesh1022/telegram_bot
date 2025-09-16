#!/usr/bin/env python3
"""
Test script to demonstrate WhatsApp bot responses for different HOD statuses
"""

from app import create_app
from app.models import db, HODStatus
from app.whatsapp_service import WhatsAppService
from datetime import datetime

def test_status_responses():
    """Test bot responses for different HOD statuses"""
    app = create_app()
    
    with app.app_context():
        print("=== Testing WhatsApp Bot Responses for Different HOD Statuses ===\n")
        
        whatsapp_service = WhatsAppService("test", "123", "test")
        hod = HODStatus.query.filter_by(hod_name="Dr. Manoj V. Bramhe").first()
        
        if not hod:
            print("❌ No HOD record found!")
            return
        
        # Test Status 1: Present and Free
        hod.status = "present_and_free"
        hod.status_message = "Available for meetings and consultations"
        hod.timestamp = datetime.utcnow()
        hod.updated_by = "admin"
        db.session.commit()
        
        print("🟢 Status: Present and Free")
        response = whatsapp_service.generate_response("hod status")
        print(f"Bot Response:\n{response}\n")
        print("-" * 60)
        
        # Test Status 2: Present and Busy
        hod.status = "present_and_busy"
        hod.status_message = "In a meeting with department faculty"
        hod.timestamp = datetime.utcnow()
        hod.updated_by = "secretary"
        db.session.commit()
        
        print("🟡 Status: Present and Busy")
        response = whatsapp_service.generate_response("is hod available")
        print(f"Bot Response:\n{response}\n")
        print("-" * 60)
        
        # Test Status 3: Not Present
        hod.status = "not_present"
        hod.status_message = "Gone for lunch, will be back by 2 PM"
        hod.timestamp = datetime.utcnow()
        hod.updated_by = "office_staff"
        db.session.commit()
        
        print("🔴 Status: Not Present")
        response = whatsapp_service.generate_response("office status")
        print(f"Bot Response:\n{response}\n")
        print("-" * 60)
        
        # Reset to default status
        hod.status = "present_and_free"
        hod.status_message = "Available for meetings and consultations"
        hod.timestamp = datetime.utcnow()
        hod.updated_by = "admin"
        db.session.commit()
        
        print("✅ Reset to default status: Present and Free")

if __name__ == '__main__':
    test_status_responses()