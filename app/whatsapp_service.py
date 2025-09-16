"""
WhatsApp Bot Service for HOD Status System
Handles WhatsApp API integration with Facebook Business API
"""

import requests
import json
import logging
from datetime import datetime
from .models import HODStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WhatsAppService:
    def __init__(self, access_token, phone_number_id, verify_token):
        self.access_token = access_token
        self.phone_number_id = phone_number_id
        self.verify_token = verify_token
        self.api_url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    def verify_webhook(self, mode, token, challenge):
        """Verify webhook subscription"""
        if mode == "subscribe" and token == self.verify_token:
            logger.info("Webhook verified successfully")
            return challenge
        logger.warning("Webhook verification failed")
        return None
    
    def send_message(self, to_number, message):
        """Send text message via WhatsApp Business API"""
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "text",
            "text": {"body": message}
        }
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            logger.info(f"Message sent successfully to {to_number}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    def send_template_message(self, to_number, template_name, language_code="en"):
        """Send template message via WhatsApp Business API"""
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code}
            }
        }
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            logger.info(f"Template message sent successfully to {to_number}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send template message: {e}")
            return False
    
    def process_incoming_message(self, webhook_data):
        """Process incoming WhatsApp message and generate response"""
        try:
            entry = webhook_data.get("entry", [])[0]
            changes = entry.get("changes", [])[0]
            value = changes.get("value", {})
            
            if "messages" in value:
                message = value["messages"][0]
                from_number = message["from"]
                message_body = message.get("text", {}).get("body", "").lower().strip()
                
                logger.info(f"Received message from {from_number}: {message_body}")
                
                # Generate response based on message content
                response = self.generate_response(message_body)
                
                # Send response
                self.send_message(from_number, response)
                
                return True
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return False
    
    def generate_response(self, message_body):
        """Generate appropriate response based on incoming message"""
        message_body = message_body.lower().strip()
        
        # Keywords for HOD status inquiry
        status_keywords = [
            "hod", "status", "available", "free", "busy", 
            "present", "office", "cabin", "dr manoj", "manoj",
            "head of department", "computer science", "cse"
        ]
        
        # Check if message is asking about HOD status
        if any(keyword in message_body for keyword in status_keywords):
            return self.get_hod_status_response()
        
        # Help commands
        elif any(word in message_body for word in ["help", "commands", "menu"]):
            return self.get_help_response()
        
        # Greeting
        elif any(word in message_body for word in ["hi", "hello", "hey", "start"]):
            return self.get_greeting_response()
        
        # Default response
        else:
            return self.get_default_response()
    
    def get_hod_status_response(self):
        """Get current HOD status from database and format response"""
        try:
            hod = HODStatus.query.filter_by(hod_name="Dr. Manoj V. Bramhe").first()
            
            if not hod:
                return "❌ Sorry, HOD information is not available at the moment."
            
            # Format status message
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
            
            response = f"""🏫 *HOD Status - Computer Science Engineering*

👨‍🏫 *Name:* Dr. Manoj V. Bramhe
{emoji} *Status:* {status}

📝 *Message:* {hod.status_message or 'No additional message'}

🕒 *Last Updated:* {hod.timestamp.strftime('%d/%m/%Y at %I:%M %p')}
👤 *Updated by:* {hod.updated_by or 'System'}

---
💡 Type 'help' for more commands"""
            
            return response
            
        except Exception as e:
            logger.error(f"Error fetching HOD status: {e}")
            return "❌ Sorry, there was an error fetching the HOD status. Please try again later."
    
    def get_help_response(self):
        """Get help message with available commands"""
        return """🤖 *HOD Status Bot - Help*

Available commands:
• *status* - Get current HOD status
• *hod* - Get HOD information  
• *office* - Check if HOD is in office
• *available* - Check HOD availability
• *help* - Show this help message

Just type any of these words and I'll help you! 

🏫 *About:* This bot provides real-time status updates for Dr. Manoj V. Bramhe, HOD of Computer Science Engineering Department."""
    
    def get_greeting_response(self):
        """Get greeting message"""
        return """👋 *Hello! Welcome to HOD Status Bot*

I can help you check the current status of:
👨‍🏫 *Dr. Manoj V. Bramhe*
🏫 *HOD, Computer Science Engineering*

📱 Simply ask:
• "What's the HOD status?"
• "Is HOD available?"
• "HOD office status"

Type 'help' for more commands! 🤖"""
    
    def get_default_response(self):
        """Get default response for unrecognized messages"""
        return """🤔 I didn't quite understand that.

Try asking:
• "HOD status" - for current status
• "Is HOD available?" - for availability
• "help" - for all commands

I'm here to help with HOD status inquiries! 🤖"""