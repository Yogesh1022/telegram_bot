# WhatsApp Bot Setup Guide for HOD Status System

## Overview
This guide will help you set up the WhatsApp bot integration with Facebook Business API to provide HOD status updates via WhatsApp.

## Prerequisites
1. Facebook Developer Account
2. WhatsApp Business Account
3. Phone number verified with WhatsApp Business API
4. ngrok or similar tunneling service for local development

## Setup Steps

### 1. Facebook Developer Console Configuration
From your screenshot, you already have:
- **App ID**: 1310861667114675
- **Phone Number ID**: 744278420647710  
- **WhatsApp Business Account ID**: 566426316491462

### 2. Generate Access Token
1. In Facebook Developer Console, go to your app
2. Click "Generate access token" button (as shown in your screenshot)
3. Copy the generated token

### 3. Configure Environment Variables
1. Copy `.env.example` to `.env`
2. Update the following values in `.env`:
```bash
WHATSAPP_ACCESS_TOKEN=EAAxxxxxxxxxxxxxxxxx  # Your generated token
WHATSAPP_PHONE_NUMBER_ID=744278420647710
WHATSAPP_VERIFY_TOKEN=hod_status_verify_token
WHATSAPP_BUSINESS_ACCOUNT_ID=566426316491462
```

### 4. Set up Webhook URL
1. Install ngrok: `npm install -g ngrok` or download from ngrok.com
2. Start your Flask app: `python run.py`
3. In another terminal, run: `ngrok http 5001`
4. Copy the https URL (e.g., https://abc123.ngrok.io)
5. In Facebook Developer Console, set webhook URL to: `https://abc123.ngrok.io/webhook/whatsapp`
6. Set verify token to: `hod_status_verify_token`

### 5. Test the Bot
1. Send a message to your WhatsApp Business number
2. Try these commands:
   - "hod status"
   - "is hod available"
   - "office status"
   - "help"

## API Endpoints

### WhatsApp Bot Endpoints
- `GET /webhook/whatsapp` - Webhook verification
- `POST /webhook/whatsapp` - Receive WhatsApp messages
- `POST /api/v1/whatsapp/send` - Send message manually
- `GET /api/v1/whatsapp/test` - Test bot responses

### HOD Status Endpoints
- `GET /api/v1/hod/status` - Get all HOD statuses
- `PUT /api/v1/hod/status/1` - Update HOD status
- `POST /api/v1/hod/status` - Create new HOD status

## Bot Commands

Users can send these messages to get HOD status:
- "hod status" / "hod" / "status"
- "is hod available" / "available"
- "office" / "cabin" / "present"
- "dr manoj" / "manoj"
- "help" - Show available commands

## Response Format

The bot responds with formatted messages including:
- 🟢 Present and Free
- 🟡 Present but Busy  
- 🔴 Not Present in Cabin
- Last updated timestamp
- Additional status message

## Troubleshooting

### Common Issues
1. **Webhook verification fails**: Check verify token matches
2. **Messages not received**: Ensure webhook URL is accessible
3. **Access token errors**: Regenerate token in Facebook Console
4. **Database errors**: Check if HOD record exists in database

### Debug Endpoints
- `GET /api/v1/whatsapp/test` - Test bot functionality
- `GET /api/v1/hod/status` - Check database status

## Security Notes
1. Never commit `.env` file to git
2. Use environment variables for sensitive data
3. Validate webhook signatures in production
4. Use HTTPS for webhook URLs

## Support
For issues, check the Flask app logs and WhatsApp Business API documentation.