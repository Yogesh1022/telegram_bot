from flask import Blueprint, jsonify, render_template, request
from datetime import datetime
from .models import db, HODStatus
from .whatsapp_service import WhatsAppService
import os

bp = Blueprint('app', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/api/v1/status', methods=['GET'])
def status():
    return jsonify({
        'status': 'running',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })

# HOD Status Routes
@bp.route('/api/v1/hod/status', methods=['GET'])
def get_all_hod_status():
    """Get status of all HODs"""
    try:
        hods = HODStatus.query.all()
        return jsonify({
            'success': True,
            'data': [hod.to_dict() for hod in hods],
            'total': len(hods)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/v1/hod/status/<int:hod_id>', methods=['GET'])
def get_hod_status(hod_id):
    """Get status of a specific HOD by ID"""
    try:
        hod = HODStatus.query.get_or_404(hod_id)
        return jsonify({
            'success': True,
            'data': hod.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404

@bp.route('/api/v1/hod/status/<int:hod_id>', methods=['PUT'])
def update_hod_status(hod_id):
    """Update HOD status"""
    try:
        hod = HODStatus.query.get_or_404(hod_id)
        data = request.get_json()
        
        # Update fields if provided
        if 'status' in data:
            # Validate status values
            valid_statuses = ['present_and_free', 'present_and_busy', 'not_present']
            if data['status'] not in valid_statuses:
                return jsonify({
                    'success': False,
                    'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
                }), 400
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

@bp.route('/api/v1/hod/status', methods=['POST'])
def create_hod_status():
    """Create a new HOD status entry"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['hod_name', 'department', 'status']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Validate status values
        valid_statuses = ['present_and_free', 'present_and_busy', 'not_present']
        if data['status'] not in valid_statuses:
            return jsonify({
                'success': False,
                'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
            }), 400
        
        # Create new HOD status
        new_hod = HODStatus(
            hod_name=data['hod_name'],
            department=data['department'],
            status=data['status'],
            status_message=data.get('status_message', ''),
            updated_by=data.get('updated_by', 'system')
        )
        
        db.session.add(new_hod)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'HOD status created successfully',
            'data': new_hod.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/v1/hod/status/<int:hod_id>', methods=['DELETE'])
def delete_hod_status(hod_id):
    """Delete a HOD status entry"""
    try:
        hod = HODStatus.query.get_or_404(hod_id)
        db.session.delete(hod)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'HOD status deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# WhatsApp Bot Webhook Routes
@bp.route('/webhook/whatsapp', methods=['GET', 'POST'])
def whatsapp_webhook():
    """WhatsApp webhook endpoint for receiving messages"""
    
    # Initialize WhatsApp service
    access_token = os.getenv('WHATSAPP_ACCESS_TOKEN', 'your_access_token_here')
    phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID', '744278420647710')  # From your screenshot
    verify_token = os.getenv('WHATSAPP_VERIFY_TOKEN', 'hod_status_verify_token')
    
    whatsapp_service = WhatsAppService(access_token, phone_number_id, verify_token)
    
    if request.method == 'GET':
        # Webhook verification
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        verified_challenge = whatsapp_service.verify_webhook(mode, token, challenge)
        if verified_challenge:
            return verified_challenge
        else:
            return 'Verification failed', 403
    
    elif request.method == 'POST':
        # Process incoming message
        try:
            webhook_data = request.get_json()
            
            # Log incoming webhook data for debugging
            print(f"Received webhook data: {webhook_data}")
            
            # Process the message
            success = whatsapp_service.process_incoming_message(webhook_data)
            
            if success:
                return jsonify({'status': 'success'}), 200
            else:
                return jsonify({'status': 'error'}), 500
                
        except Exception as e:
            print(f"Error processing WhatsApp webhook: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

@bp.route('/api/v1/whatsapp/send', methods=['POST'])
def send_whatsapp_message():
    """Manual endpoint to send WhatsApp messages (for testing)"""
    try:
        data = request.get_json()
        
        if 'to' not in data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: to, message'
            }), 400
        
        # Initialize WhatsApp service
        access_token = os.getenv('WHATSAPP_ACCESS_TOKEN', 'your_access_token_here')
        phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID', '744278420647710')
        verify_token = os.getenv('WHATSAPP_VERIFY_TOKEN', 'hod_status_verify_token')
        
        whatsapp_service = WhatsAppService(access_token, phone_number_id, verify_token)
        
        success = whatsapp_service.send_message(data['to'], data['message'])
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Message sent successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to send message'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/v1/whatsapp/test', methods=['GET'])
def test_whatsapp_bot():
    """Test endpoint to check WhatsApp bot functionality"""
    try:
        # Simulate a status request message
        test_message = "hod status"
        
        access_token = os.getenv('WHATSAPP_ACCESS_TOKEN', 'your_access_token_here')
        phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID', '744278420647710')
        verify_token = os.getenv('WHATSAPP_VERIFY_TOKEN', 'hod_status_verify_token')
        
        whatsapp_service = WhatsAppService(access_token, phone_number_id, verify_token)
        response = whatsapp_service.generate_response(test_message)
        
        return jsonify({
            'success': True,
            'test_message': test_message,
            'bot_response': response,
            'config': {
                'phone_number_id': phone_number_id,
                'has_access_token': bool(access_token and access_token != 'your_access_token_here')
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    

