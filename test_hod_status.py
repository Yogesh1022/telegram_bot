#!/usr/bin/env python3
"""
Test script to demonstrate HOD status database functionality
"""

from app import create_app
from app.models import db, HODStatus
from datetime import datetime

def test_hod_status():
    """Test HOD status operations"""
    app = create_app()
    
    with app.app_context():
        print("=== HOD Status Database Test ===\n")
        
        # Get current HOD status
        hod = HODStatus.query.filter_by(hod_name="Dr. Manoj V. Bramhe").first()
        if hod:
            print(f"Current HOD Status:")
            print(f"Name: {hod.hod_name}")
            print(f"Department: {hod.department}")
            print(f"Status: {hod.status}")
            print(f"Message: {hod.status_message}")
            print(f"Last Updated: {hod.timestamp}")
            print(f"Updated By: {hod.updated_by}")
            print()
            
            # Test status updates
            print("Testing status updates...")
            
            # Update to busy
            hod.status = "present_and_busy"
            hod.status_message = "In a meeting with students"
            hod.timestamp = datetime.utcnow()
            hod.updated_by = "secretary"
            db.session.commit()
            print(f"✅ Updated status to: {hod.status}")
            
            # Update to not present
            hod.status = "not_present"
            hod.status_message = "Gone for lunch"
            hod.timestamp = datetime.utcnow()
            hod.updated_by = "office_staff"
            db.session.commit()
            print(f"✅ Updated status to: {hod.status}")
            
            # Update back to free
            hod.status = "present_and_free"
            hod.status_message = "Available for meetings and consultations"
            hod.timestamp = datetime.utcnow()
            hod.updated_by = "admin"
            db.session.commit()
            print(f"✅ Updated status to: {hod.status}")
            
            print(f"\nFinal Status: {hod.status}")
            print(f"Last Updated: {hod.timestamp}")
        else:
            print("❌ No HOD record found. Please run db_init.py first.")
        
        print("\n=== Valid Status Options ===")
        print("1. present_and_free - HOD is Present and Free")
        print("2. present_and_busy - HOD is Present and Busy")
        print("3. not_present - HOD is not Present in cabin")

if __name__ == '__main__':
    test_hod_status()