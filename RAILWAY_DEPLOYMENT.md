# Railway.app Deployment Guide

## 🚀 Deploy HOD Status WhatsApp Bot to Railway

This guide walks you through deploying your HOD Status WhatsApp Bot to Railway.app for production use.

## 📋 Prerequisites

1. [Railway.app](https://railway.app) account
2. GitHub repository with your code
3. WhatsApp Business API tokens from Facebook Developer Console

## 🛠️ Deployment Steps

### 1. Prepare Your Repository

1. Ensure all files are committed to your GitHub repository:
   - `main.py` (combined application)
   - `Dockerfile`
   - `requirements.txt`
   - `railway.toml`
   - All `app/` directory files

### 2. Deploy to Railway

1. **Login to Railway.app**
   - Visit [railway.app](https://railway.app)
   - Login with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Configure Environment Variables**
   Go to your project settings and add these environment variables:

   ```
   WHATSAPP_ACCESS_TOKEN=EAAxxxxxxxxxxxxxxxxxxxx
   WHATSAPP_PHONE_NUMBER_ID=744278420647710
   WHATSAPP_VERIFY_TOKEN=CE_HOD123
   WHATSAPP_BUSINESS_ACCOUNT_ID=566426316491462
   SECRET_KEY=your-super-secret-production-key
   PORT=5001
   DEBUG=false
   ```

4. **Deploy**
   - Railway will automatically build and deploy your app
   - Wait for deployment to complete

### 3. Configure WhatsApp Webhook

1. **Get Your Railway URL**
   - Copy your Railway app URL (e.g., `https://your-app-name.railway.app`)

2. **Update Facebook Developer Console**
   - Go to your WhatsApp Business API setup
   - Set Webhook URL to: `https://your-app-name.railway.app/webhook/whatsapp`
   - Set Verify Token to: `CE_HOD123`
   - Subscribe to webhook events

### 4. Test Your Deployment

1. **Health Check**
   - Visit: `https://your-app-name.railway.app/health`
   - Should return: `{"status": "healthy", ...}`

2. **API Test**
   - Visit: `https://your-app-name.railway.app/api/status`
   - Should return HOD status data

3. **WhatsApp Test**
   - Send a message to your WhatsApp Business number
   - Try: "hod status", "help", "hi"

## 🔧 Configuration Files

### main.py
- Combined Flask application
- Handles webhook verification and message processing
- Production-ready with proper logging

### Dockerfile
- Multi-stage build for efficiency
- Health checks included
- Security optimizations

### requirements.txt
- All necessary Python packages
- Production dependencies included

### railway.toml
- Railway-specific configuration
- Build and start commands
- Environment variable documentation

## 📱 WhatsApp Bot Commands

Once deployed, users can interact with your bot using:

- **"hod status"** - Get current HOD status
- **"is hod available"** - Check availability
- **"office"** - Check office presence
- **"help"** - Show available commands
- **"hi"** - Get greeting and introduction

## 🔄 Status Management

### Update HOD Status via API

```bash
curl -X POST https://your-app-name.railway.app/api/status \
  -H "Content-Type: application/json" \
  -d '{
    "status": "present_and_busy",
    "status_message": "In department meeting until 3 PM",
    "updated_by": "secretary"
  }'
```

### Valid Status Values
- `present_and_free` - 🟢 HOD is Present and Free
- `present_and_busy` - 🟡 HOD is Present and Busy
- `not_present` - 🔴 HOD is not Present in cabin

## 🚨 Troubleshooting

### Common Issues

1. **Webhook Verification Failed**
   - Check verify token matches exactly: `CE_HOD123`
   - Ensure Railway URL is accessible

2. **Database Issues**
   - Railway automatically creates SQLite database
   - Check logs for initialization errors

3. **WhatsApp API Issues**
   - Verify access token is valid
   - Check phone number ID is correct
   - Ensure webhook URL is HTTPS

### Monitoring

- **Railway Logs**: View in Railway dashboard
- **Health Endpoint**: `https://your-app-name.railway.app/health`
- **API Status**: `https://your-app-name.railway.app/api/status`

## 🔐 Security

- Environment variables are encrypted in Railway
- HTTPS is automatically provided
- Database is isolated per deployment
- Access tokens are never logged

## 💰 Railway Pricing

- **Hobby Plan**: $5/month (recommended for this app)
- **Pro Plan**: $20/month (for higher traffic)
- Free trial available

## 📞 Support

- Railway Documentation: [docs.railway.app](https://docs.railway.app)
- WhatsApp Business API: [developers.facebook.com](https://developers.facebook.com)

---

Your HOD Status WhatsApp Bot is now live and ready to serve users! 🎉