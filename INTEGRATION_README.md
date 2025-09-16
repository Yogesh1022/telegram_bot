# HOD Detection System - Telegram Bot Integration with 10-Second Stability Analysis

This system integrates computer vision-based HOD detection with a Telegram bot to provide real-time status updates using a 10-second stability buffer to eliminate flickering and provide reliable status determination.

## 🎯 Status Logic with Stability Analysis

The system uses a **10-second majority vote** approach to determine stable HOD status:

### Stability Buffer Process
1. **Continuous Frame Analysis**: Every frame from webcam is analyzed for HOD presence and person count
2. **10-Second Buffer**: System maintains a buffer of the last 10 seconds of detection data
3. **Majority Vote**: Status is determined by what was detected in >50% of frames over 10 seconds
4. **Update Interval**: Final status is updated every 10 seconds based on analysis

### Case 1: HOD Present and Free 🟢
- **Condition**: HOD detected in >50% of frames + Average other persons ≤ 0.5
- **Status**: `present_and_free`
- **Message**: "Available for meetings and consultations"

### Case 2: HOD Present but Busy 🟡
- **Condition**: HOD detected in >50% of frames + Average other persons > 0.5
- **Status**: `present_and_busy` 
- **Message**: "Currently busy - average X other person(s) present"

### Case 3: HOD Not Present 🔴
- **Condition**: HOD detected in ≤50% of frames over 10 seconds
- **Status**: `not_present`
- **Message**: "Not available in cabin"

### Case 4: System Offline ⚫
- **Condition**: No updates from detection system for >30 seconds
- **Status**: `system_offline`
- **Message**: "Detection system is offline"

## 📁 Files Structure

```
flask-app/
├── detection_status.py                    # Status management with 10-sec stability buffer
├── run_live_detection_integrated.py     # Enhanced detection script with stability analysis
├── telegrambot_integrated.py            # Enhanced Telegram bot with stability info
├── test_stability_integration.py        # Stability analysis test script
└── requirements.txt                     # Dependencies
```

## 🔧 Installation & Setup

### 1. Install Compatible Dependencies
```bash
# Install compatible httpx version for telegram bot
pip install "httpx==0.24.1" "httpcore==0.17.3"

# Install all other requirements
pip install -r requirements.txt
```

### 2. Required Files for Detection
Make sure you have these files in your project directory:
- `yolov5n.onnx` - YOLO model for person detection
- `hod_encoding.pickle` - HOD facial encodings

### 3. Telegram Bot Setup
1. Create a bot with @BotFather on Telegram
2. Get your bot token
3. Create `.env` file:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

## 🚀 Usage

### Running the Complete System

1. **Start the Detection System**:
```bash
python run_live_detection_integrated.py
```

2. **In Another Terminal, Start the Telegram Bot**:
```bash
python telegrambot_integrated.py
```

### Testing the Integration

Run the test script to simulate different scenarios:
```bash
python test_integration.py
```

## 💬 Telegram Bot Commands

### Basic Commands
- `/start` - Welcome message and overview
- `/status` - Get current HOD status
- `/help` - Show all available commands
- `/quick` - Quick status update buttons

### Text Queries
Users can simply type these words to get status:
- "status", "hod", "available", "free"
- "busy", "present", "office", "cabin"
- "dr manoj", "computer science", "cse"

### Admin Commands
- `/update <status> <message>` - Manually update status
- Valid statuses: `present_and_free`, `present_and_busy`, `not_present`

## 🔄 How 10-Second Stability Analysis Works

### Detection System → Stability Buffer
1. Detection script analyzes webcam feed continuously
2. Each frame detection is added to a 10-second rolling buffer
3. Buffer stores: timestamp, HOD presence, person count for each frame
4. Every 10 seconds, system analyzes buffer using majority vote

### Stability Analysis Process
1. **Frame Collection**: Collects ~300 frames over 10 seconds (at 30fps)
2. **Majority Vote**: HOD considered present if detected in >50% of frames
3. **Busy/Free Determination**: Averages person count when HOD is present
4. **Status Update**: Updates final status based on analysis

### Telegram Bot → Status Response
1. Bot receives status query from user
2. Reads latest analyzed status from stability system
3. Shows detailed analysis information (frames analyzed, detection rate)
4. Falls back to database if detection system offline

### Status File Format
```json
{
  "hod_present": true,
  "total_persons": 2,
  "other_persons": 1,
  "status": "present_and_busy",
  "message": "Currently busy - 1 other person(s) present",
  "timestamp": "2025-09-16T10:30:45",
  "last_update": 1726485045.123
}
```

## 📱 Bot Response Examples

### When Detection System is Active (with 10-sec analysis):
```
🏫 HOD Status - Computer Science Engineering

👨‍🏫 Name: Dr. Manoj V. Bramhe
🟡 Status: Present but Busy

📍 Live Detection Info (10-sec analysis):
• HOD Present: Yes
• Total Persons in Frame: 3
• Other Persons: 2

📊 Stability Analysis:
• Frames Analyzed: 285
• HOD Detection Rate: 78.9%
• Analysis Duration: 10.0s

📝 Message: Currently busy - average 1.8 other person(s) present

🕒 Last Updated: 16/09/2025 at 10:30 AM
🤖 Updated by: live_detection_system

🔴 Live detection system is ACTIVE (10-sec stability buffer)
```

### When Detection System is Offline:
```
🏫 HOD Status - Computer Science Engineering

👨‍🏫 Name: Dr. Manoj V. Bramhe
🔴 Status: Not Present in Cabin

📝 Message: Last known status from database

🕒 Last Updated: 16/09/2025 at 09:15 AM
👤 Updated by: System

⚠️ Live detection system is OFFLINE - showing database status

Use /update to change status manually or /help for more commands
```

## 🛠️ Troubleshooting

### HTTPx Compatibility Error
If you get `TypeError: AsyncClient.__init__() got an unexpected keyword argument 'proxies'`:
```bash
pip uninstall -y httpx httpcore
pip install "httpx==0.24.1" "httpcore==0.17.3"
```

### Detection System Not Working
1. Check if webcam is connected and accessible
2. Verify YOLO model file exists: `yolov5n.onnx`
3. Verify HOD encoding file exists: `hod_encoding.pickle`
4. Install OpenCV: `pip install opencv-python`
5. Install face recognition: `pip install face-recognition`

### Bot Not Responding
1. Check if bot token is correct in `.env`
2. Verify Flask app modules can be imported
3. Check database connection
4. Ensure compatible httpx version is installed

## 🎥 Demo Workflow

1. **Setup**: Start detection system and bot
2. **Test Case 1**: HOD sits alone → Bot shows "Present and Free"
3. **Test Case 2**: Visitor joins HOD → Bot shows "Present but Busy"
4. **Test Case 3**: HOD leaves → Bot shows "Not Present"
5. **Test Case 4**: Stop detection → Bot shows "System Offline"

## 📊 Performance Notes

- Detection updates every ~30 frames (≈1 second at 30fps)
- Status considered offline after 30 seconds without updates
- Bot uses real-time data when available, database as fallback
- Optimized for Raspberry Pi 4B deployment

## 🔐 Security Features

- Manual override capability through Telegram commands
- Database backup when detection system is offline
- Timestamp tracking for all status updates
- User attribution for manual updates