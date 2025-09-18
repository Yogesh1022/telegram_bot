import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, CallbackQueryHandler
)
from detection_status import DetectionStatusManager

# Load environment variables
load_dotenv()

# Ensure we can import Flask app modules
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

try:
    from app import create_app
    from app.models import db, HODStatus
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you have 'app/__init__.py', 'app/models.py', and Flask installed.")
    sys.exit(1)

# Telegram token from .env (fallback included)
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    print("⚠️ No TELEGRAM_BOT_TOKEN found in .env, using fallback token")
    TOKEN = ""

# ------------------ BOT LOGIC ------------------ #
class HODTelegramBot:
    def __init__(self):
        self.app = create_app()
        self.detection_manager = DetectionStatusManager()

    def get_hod_status(self):
        """Get HOD status from detection system first, fallback to database"""
        # Try to get real-time status from detection system
        detection_status = self.detection_manager.get_current_status()
        
        if detection_status:
            # Use real-time detection data
            return {
                'hod_name': "Dr. Manoj V. Bramhe",
                'status': detection_status['status'],
                'status_message': detection_status['message'],
                'timestamp': datetime.fromisoformat(detection_status['timestamp']),
                'updated_by': 'live_detection_system',
                'detection_data': {
                    'hod_present': detection_status['hod_present'],
                    'total_persons': detection_status['total_persons'],
                    'other_persons': detection_status['other_persons']
                }
            }
        else:
            # Fallback to database if detection system is offline
            with self.app.app_context():
                try:
                    hod_db = HODStatus.query.filter_by(hod_name="Dr. Manoj V. Bramhe").first()
                    if hod_db:
                        return {
                            'hod_name': hod_db.hod_name,
                            'status': hod_db.status,
                            'status_message': hod_db.status_message,
                            'timestamp': hod_db.timestamp,
                            'updated_by': hod_db.updated_by,
                            'detection_data': None
                        }
                except Exception as e:
                    print(f"Error fetching HOD status from database: {e}")
            return None

    def update_hod_status(self, status, message, updated_by="telegram_bot"):
        """Update HOD status in database (for manual updates)"""
        with self.app.app_context():
            try:
                hod = HODStatus.query.filter_by(hod_name="Dr. Manoj V. Bramhe").first()
                if hod:
                    hod.status = status
                    hod.status_message = message
                    hod.timestamp = datetime.utcnow()
                    hod.updated_by = updated_by
                    db.session.commit()
                    return True
                return False
            except Exception as e:
                print(f"Error updating HOD status: {e}")
                return False

    def format_status_message(self, hod_data):
        """Format HOD status for Telegram message with detection info"""
        if not hod_data:
            return "❌ Sorry, HOD information is not available at the moment."

        # Status emojis and text
        status_emoji = {
            "present_and_free": "🟢",
            "present_and_busy": "🟡",
            "not_present": "🔴",
            "system_offline": "⚫"
        }
        status_text = {
            "present_and_free": "Present and Free",
            "present_and_busy": "Present but Busy",
            "not_present": "Not Present in Cabin",
            "system_offline": "Detection System Offline"
        }

        emoji = status_emoji.get(hod_data['status'], "⚪")
        status = status_text.get(hod_data['status'], hod_data['status'])

        # Build message based on whether detection data is available
        if hod_data.get('detection_data'):
            # Real-time detection data available
            detection = hod_data['detection_data']
            stability = hod_data.get('stability_analysis', {})
            
            message = f"""🏫 HOD Status - Computer Science Engineering

👨‍🏫 Name: Dr. Manoj V. Bramhe
{emoji} Status: {status}

📍 Live Detection Info (10-sec analysis):
• HOD Present: {'Yes' if detection['hod_present'] else 'No'}
• Total Persons in Frame: {detection['total_persons']}
• Other Persons: {detection['other_persons']}

� Stability Analysis:
• Frames Analyzed: {stability.get('frames_analyzed', 'N/A')}
• HOD Detection Rate: {stability.get('hod_detection_percentage', 0):.1f}%
• Analysis Duration: {stability.get('buffer_duration_actual', 0):.1f}s

�📝 Message: {hod_data['status_message']}

🕒 Last Updated: {hod_data['timestamp'].strftime('%d/%m/%Y at %I:%M %p')}
🤖 Updated by: {hod_data['updated_by']}

🔴 Live detection system is ACTIVE (10-sec stability buffer)"""
        else:
            # Fallback to database data
            message = f"""🏫 HOD Status - Computer Science Engineering

👨‍🏫 Name: Dr. Manoj V. Bramhe
{emoji} Status: {status}

📝 Message: {hod_data['status_message'] or 'No additional message'}

🕒 Last Updated: {hod_data['timestamp'].strftime('%d/%m/%Y at %I:%M %p')}
👤 Updated by: {hod_data['updated_by'] or 'System'}

⚠️ Live detection system is OFFLINE - showing database status

Use /update to change status manually or /help for more commands"""
        
        return message

# Initialize bot instance
bot_instance = HODTelegramBot()

# ------------------ HANDLERS ------------------ #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    welcome_message = """👋 Welcome to HOD Status Bot!

I can help you check and update the status of:
👨‍🏫 Dr. Manoj V. Bramhe
🏫 HOD, Computer Science Engineering

Available Commands:
📊 /status - Get current HOD status
🔄 /update - Update HOD status
📱 /quick - Quick status buttons
❓ /help - Show all commands

Just type 'status' to get the current status!"""
    
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command handler"""
    help_text = """🤖 HOD Status Bot - Help

Available Commands:
📊 /status - Get current HOD status
🔄 /update - Update HOD status (admin only)
📱 /quick - Quick status update buttons
❓ /help - Show this help message

Text Commands:
Just type any of these keywords:
• "status" or "hod" - Get current status
• "available" or "free" - Check availability
• "office" or "cabin" - Check office presence
• "busy" or "meeting" - Check if in meeting

Status Options:
🟢 Present and Free
🟡 Present but Busy
🔴 Not Present in Cabin

Live Detection Features:
🤖 Real-time computer vision detection
📹 Webcam-based HOD presence monitoring
👥 Person counting in office cabin
⚡ Automatic status updates

Admin Features:
Use /update command to change HOD status manually
Format: /update <status> <message>
Example: /update present_and_busy In faculty meeting"""
    
    await update.message.reply_text(help_text)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Status command handler"""
    hod_data = bot_instance.get_hod_status()
    status_message = bot_instance.format_status_message(hod_data)
    
    # Add quick action buttons
    keyboard = [
        [
            InlineKeyboardButton("🔄 Refresh Status", callback_data="refresh_status"),
            InlineKeyboardButton("📱 Quick Update", callback_data="quick_update")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(status_message, reply_markup=reply_markup)

async def quick_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Quick status update buttons"""
    keyboard = [
        [InlineKeyboardButton("🟢 Present & Free", callback_data="status_present_and_free")],
        [InlineKeyboardButton("🟡 Present & Busy", callback_data="status_present_and_busy")],
        [InlineKeyboardButton("🔴 Not Present", callback_data="status_not_present")],
        [InlineKeyboardButton("📊 View Current Status", callback_data="refresh_status")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🔄 Quick Status Update\n\nSelect the current HOD status:",
        reply_markup=reply_markup
    )

async def update_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Update HOD status command"""
    if not context.args:
        await update.message.reply_text(
            "🔄 Update HOD Status\n\n"
            "Usage: /update <status> <message>\n\n"
            "Valid statuses:\n"
            "• present_and_free\n"
            "• present_and_busy\n"
            "• not_present\n\n"
            "Example:\n"
            "/update present_and_busy In faculty meeting\n\n"
            "Or use /quick for button interface"
        )
        return
    
    valid_statuses = ['present_and_free', 'present_and_busy', 'not_present']
    status = context.args[0].lower()
    
    if status not in valid_statuses:
        await update.message.reply_text(
            f"❌ Invalid status: {status}\n\n"
            f"Valid options: {', '.join(valid_statuses)}"
        )
        return
    
    # Get status message (everything after the status)
    message = " ".join(context.args[1:]) if len(context.args) > 1 else "Status updated via Telegram bot"
    
    # Update status
    username = update.effective_user.username or update.effective_user.first_name
    success = bot_instance.update_hod_status(status, message, f"telegram_user_{username}")
    
    if success:
        await update.message.reply_text(
            f"✅ Status Updated Successfully!\n\n"
            f"New Status: {status.replace('_', ' ').title()}\n"
            f"Message: {message}"
        )
        
        # Send updated status
        hod_data = bot_instance.get_hod_status()
        status_message = bot_instance.format_status_message(hod_data)
        await update.message.reply_text(status_message)
    else:
        await update.message.reply_text(
            "❌ Failed to update status. Please try again."
        )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "refresh_status":
        hod_data = bot_instance.get_hod_status()
        status_message = bot_instance.format_status_message(hod_data)
        await query.edit_message_text(status_message)
    
    elif query.data == "quick_update":
        keyboard = [
            [InlineKeyboardButton("🟢 Present & Free", callback_data="status_present_and_free")],
            [InlineKeyboardButton("🟡 Present & Busy", callback_data="status_present_and_busy")],
            [InlineKeyboardButton("🔴 Not Present", callback_data="status_not_present")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🔄 Quick Status Update\n\nSelect the current HOD status:",
            reply_markup=reply_markup
        )
    
    elif query.data.startswith("status_"):
        status = query.data.replace("status_", "")
        username = update.effective_user.username or update.effective_user.first_name
        
        status_messages = {
            "present_and_free": "Available for meetings and consultations",
            "present_and_busy": "Currently busy with work/meetings",
            "not_present": "Not available in cabin"
        }
        
        message = status_messages.get(status, "Status updated via Telegram bot")
        success = bot_instance.update_hod_status(status, message, f"telegram_user_{username}")
        
        if success:
            hod_data = bot_instance.get_hod_status()
            status_message = bot_instance.format_status_message(hod_data)
            await query.edit_message_text(
                f"✅ Status Updated!\n\n{status_message}"
            )
        else:
            await query.edit_message_text(
                "❌ Failed to update status. Please try again."
            )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages"""
    message_text = update.message.text.lower().strip()
    
    # Keywords for status inquiry
    status_keywords = [
        "status", "hod", "available", "free", "busy", 
        "present", "office", "cabin", "dr manoj", "manoj",
        "head of department", "computer science", "cse"
    ]
    
    # Check if message is asking about status
    if any(keyword in message_text for keyword in status_keywords):
        hod_data = bot_instance.get_hod_status()
        status_message = bot_instance.format_status_message(hod_data)
        
        keyboard = [
            [
                InlineKeyboardButton("🔄 Refresh", callback_data="refresh_status"),
                InlineKeyboardButton("📱 Quick Update", callback_data="quick_update")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(status_message, reply_markup=reply_markup)
    else:
        # Default response
        await update.message.reply_text(
            "🤔 I didn't quite understand that.\n\n"
            "Try asking:\n"
            "• 'HOD status' - for current status\n"
            "• 'Is HOD available?' - for availability\n"
            "• Use /help for all commands\n\n"
            "I'm here to help with HOD status inquiries! 🤖"
        )

# ------------------ MAIN ------------------ #
def main():
    """Main function to run the bot"""
    app = Application.builder().token(TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("update", update_command))
    app.add_handler(CommandHandler("quick", quick_command))
    
    # Callback query handler for buttons
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    # Text message handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("🤖 HOD Status Telegram Bot is running...")
    print("🏫 Connected to HOD database")
    print("📹 Integrated with live detection system")
    print("🔧 Optimized for Raspberry Pi 4B")
    print("📱 Bot ready to receive messages")
    
    app.run_polling()

if __name__ == "__main__":

    main()
