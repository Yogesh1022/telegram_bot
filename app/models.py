from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class HODStatus(db.Model):
    """Model to track the status of Head of Department (HOD)"""
    __tablename__ = 'hod_status'
    
    id = db.Column(db.Integer, primary_key=True)
    hod_name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='present_and_free')  # present_and_free, present_and_busy, not_present
    status_message = db.Column(db.Text)  # Optional message explaining the status
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_by = db.Column(db.String(100))  # Who updated the status
    
    def __repr__(self):
        return f'<HODStatus {self.hod_name}: {self.status}>'
    
    def to_dict(self):
        """Convert model instance to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'hod_name': self.hod_name,
            'department': self.department,
            'status': self.status,
            'status_message': self.status_message,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'updated_by': self.updated_by
        }