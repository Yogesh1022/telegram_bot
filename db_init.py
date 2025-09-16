#!/usr/bin/env python3
"""
Database initialization script for HOD status tracking system.
This script creates the database tables and populates initial data.
"""

from app import create_app
from app.models import db, HODStatus

def init_database():
    """Initialize the database with tables and sample data."""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")
        
        # Check if we already have data
        existing_hods = HODStatus.query.first()
        if existing_hods:
            print("Database already contains HOD status data.")
            return
        
        # Add sample HOD status entries
        sample_hods = [
            HODStatus(
                hod_name="Dr. Manoj V. Bramhe",
                department="Computer Science Engineering",
                status="present_and_free",
                status_message="Available for meetings and consultations",
                updated_by="admin"
            )
        ]
        
        # Add sample data to database
        for hod in sample_hods:
            db.session.add(hod)
        
        try:
            db.session.commit()
            print(f"Successfully added {len(sample_hods)} sample HOD status entries!")
        except Exception as e:
            db.session.rollback()
            print(f"Error adding sample data: {e}")

if __name__ == '__main__':
    init_database()