#!/usr/bin/env python3
"""
Production-ready Flask application for HOD Status WhatsApp Bot
Combines webhook verification and full bot functionality for Railway deployment
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from flask import Flask, request, jsonify, render_template
from datetime import datetime
import logging
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import app components
from app import create_app
from app.models import db, HODStatus
from app.whatsapp_service import WhatsAppService

# Create Flask application
app = create_app()

# Environment variables
WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN', 'your_access_token_here')
WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID', '744278420647710')
WHATSAPP_VERIFY_TOKEN = os.getenv('WHATSAPP_VERIFY_TOKEN', 'CE_HOD123')
PORT = int(os.getenv('PORT', 5001))

# Initialize WhatsApp service
whatsapp_service = WhatsAppService(
    access_token=WHATSAPP_ACCESS_TOKEN,
    phone_number_id=WHATSAPP_PHONE_NUMBER_ID,
    verify_token=WHATSAPP_VERIFY_TOKEN
)

# Root route for health check
@app.route('/')
def index():
    """Root endpoint for health check"""
    return jsonify({
        'status': 'online',
        'service': 'HOD Status WhatsApp Bot',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

@app.route('/health')
def health():
    """Health check endpoint for Railway"""
    return jsonify({
        'status': 'healthy',
        'database': 'connected',
        'whatsapp_configured': bool(WHATSAPP_ACCESS_TOKEN != 'your_access_token_here'),
        'timestamp': datetime.utcnow().isoformat()
    })

# Combined WhatsApp webhook endpoint
@app.route('/webhook/whatsapp', methods=['GET', 'POST'])
def whatsapp_webhook():
    """Combined WhatsApp webhook for verification and message processing"""
    
    if request.method == 'GET':
        # Webhook verification (simplified for Railway)
        token_sent = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        mode = request.args.get("hub.mode")
        
        logger.info(f"Webhook verification: mode={mode}, token={token_sent}")
        
        if mode == "subscribe" and token_sent == WHATSAPP_VERIFY_TOKEN:
            logger.info("Webhook verified successfully")
            return challenge, 200
        else:
            logger.warning(f"Webhook verification failed. Expected: {WHATSAPP_VERIFY_TOKEN}, Got: {token_sent}")
            return "Invalid verification token", 403
    
    elif request.method == 'POST':
        # Process incoming messages
        try:
            webhook_data = request.get_json()
            logger.info(f"Received webhook data: {webhook_data}")
            
            # Process the message using our WhatsApp service
            success = whatsapp_service.process_incoming_message(webhook_data)
            
            if success:
                return jsonify({'status': 'success'}), 200
            else:
                return jsonify({'status': 'error'}), 500
                
        except Exception as e:
            logger.error(f"Error processing WhatsApp webhook: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

# API endpoint to get HOD status
@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current HOD status"""
    try:
        hod = HODStatus.query.filter_by(hod_name="Dr. Manoj V. Bramhe").first()
        if hod:
            return jsonify({
                'success': True,
                'data': hod.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'HOD record not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# API endpoint to update HOD status
@app.route('/api/status', methods=['POST'])
def update_status():
    """Update HOD status"""
    try:
        data = request.get_json()
        
        hod = HODStatus.query.filter_by(hod_name="Dr. Manoj V. Bramhe").first()
        if not hod:
            return jsonify({
                'success': False,
                'error': 'HOD record not found'
            }), 404
        
        # Validate status
        valid_statuses = ['present_and_free', 'present_and_busy', 'not_present']
        if 'status' in data and data['status'] not in valid_statuses:
            return jsonify({
                'success': False,
                'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
            }), 400
        
        # Update fields
        if 'status' in data:
            hod.status = data['status']
        if 'status_message' in data:
            hod.status_message = data['status_message']
        if 'updated_by' in data:
            hod.updated_by = data['updated_by']
        
        hod.timestamp = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'HOD status updated successfully',
            'data': hod.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Initialize database on startup
def initialize_database():
    """Initialize database with HOD record if not exists"""
    try:
        with app.app_context():
            db.create_all()
            
            # Check if HOD record exists
            hod = HODStatus.query.filter_by(hod_name="Dr. Manoj V. Bramhe").first()
            if not hod:
                # Create default HOD record
                hod = HODStatus(
                    hod_name="Dr. Manoj V. Bramhe",
                    department="Computer Science Engineering",
                    status="present_and_free",
                    status_message="Available for meetings and consultations",
                    updated_by="system"
                )
                db.session.add(hod)
                db.session.commit()
                logger.info("Created default HOD record")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")

# Call initialization
initialize_database()

if __name__ == '__main__':
    # For Railway deployment
    app.run(host='0.0.0.0', port=PORT, debug=False)