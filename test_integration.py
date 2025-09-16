# test_integration.py
"""
Test script to demonstrate the integration between detection system and Telegram bot
This simulates the detection system updating status and shows how the bot responds
"""

import time
import json
from detection_status import DetectionStatusManager

def simulate_detection_scenarios():
    """Simulate different detection scenarios"""
    
    status_manager = DetectionStatusManager()
    
    print("🧪 Testing Detection System Integration")
    print("=" * 50)
    
    # Scenario 1: HOD alone in office (Free)
    print("\n📹 Scenario 1: HOD alone in office")
    status_manager.update_detection_status(hod_present=True, total_persons=1)
    status = status_manager.get_current_status()
    print(f"✅ Status: {status['status']}")
    print(f"📝 Message: {status['message']}")
    print(f"👥 Total persons: {status['total_persons']}, Others: {status['other_persons']}")
    
    time.sleep(2)
    
    # Scenario 2: HOD with visitors (Busy)
    print("\n📹 Scenario 2: HOD with 2 visitors")
    status_manager.update_detection_status(hod_present=True, total_persons=3)
    status = status_manager.get_current_status()
    print(f"✅ Status: {status['status']}")
    print(f"📝 Message: {status['message']}")
    print(f"👥 Total persons: {status['total_persons']}, Others: {status['other_persons']}")
    
    time.sleep(2)
    
    # Scenario 3: HOD not present
    print("\n📹 Scenario 3: HOD not in office")
    status_manager.update_detection_status(hod_present=False, total_persons=0)
    status = status_manager.get_current_status()
    print(f"✅ Status: {status['status']}")
    print(f"📝 Message: {status['message']}")
    print(f"👥 Total persons: {status['total_persons']}, Others: {status['other_persons']}")
    
    time.sleep(2)
    
    # Scenario 4: Other people in office, but not HOD
    print("\n📹 Scenario 4: Other people in office, HOD not present")
    status_manager.update_detection_status(hod_present=False, total_persons=2)
    status = status_manager.get_current_status()
    print(f"✅ Status: {status['status']}")
    print(f"📝 Message: {status['message']}")
    print(f"👥 Total persons: {status['total_persons']}, Others: {status['other_persons']}")
    
    # Wait 35 seconds to test offline detection
    print("\n⏳ Waiting 35 seconds to test offline detection...")
    time.sleep(35)
    
    # Scenario 5: System offline
    print("\n📹 Scenario 5: Detection system offline (no updates for >30 seconds)")
    status = status_manager.get_current_status()
    print(f"✅ Status: {status['status']}")
    print(f"📝 Message: {status['message']}")
    
    print("\n✅ Integration test completed!")
    print("\nTo test with Telegram bot:")
    print("1. First install the correct httpx version:")
    print("   pip install 'httpx==0.24.1' 'httpcore==0.17.3'")
    print("2. Run the detection system:")
    print("   python run_live_detection_integrated.py")
    print("3. In another terminal, run the bot:")
    print("   python telegrambot_integrated.py")
    print("4. Send 'status' to your bot on Telegram")

if __name__ == "__main__":
    simulate_detection_scenarios()