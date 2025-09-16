# test_stability_integration.py
"""
Test script to demonstrate the 10-second stability analysis integration
This simulates realistic detection scenarios with fluctuating detection results
"""

import time
import random
from detection_status import DetectionStatusManager

def simulate_realistic_detection():
    """Simulate realistic detection scenarios with some detection fluctuation"""
    
    status_manager = DetectionStatusManager()
    
    print("🧪 Testing 10-Second Stability Analysis")
    print("=" * 60)
    print("This test simulates realistic camera detection with some fluctuation")
    print("Status will be determined by majority vote over 10-second windows")
    print()
    
    # Test Scenario 1: HOD mostly alone (should result in "free")
    print("📹 Scenario 1: HOD mostly alone in office (occasional detection misses)")
    print("Expected result: present_and_free")
    print("-" * 50)
    
    for i in range(120):  # 12 seconds of data
        # 80% of time HOD is detected alone, 20% detection misses or false positives
        if random.random() < 0.8:
            hod_present = True
            total_persons = 1
        else:
            # Occasional detection miss or false extra person
            if random.random() < 0.5:
                hod_present = False
                total_persons = 0
            else:
                hod_present = True
                total_persons = 2  # False positive extra person
        
        status_manager.add_detection_frame(hod_present, total_persons)
        
        # Print analysis every 2 seconds
        if i % 20 == 19:
            buffer_info = status_manager.get_buffer_info()
            if isinstance(buffer_info, dict):
                print(f"  Frame {i+1:3d}: Buffer has {buffer_info['total_frames']} frames, "
                      f"HOD detected in {buffer_info['hod_percentage']:.1f}% of frames")
        
        time.sleep(0.1)  # Simulate ~10fps
    
    # Analyze final result
    result = status_manager.analyze_stability_buffer()
    if result:
        print(f"\n✅ Final Result: {result['status']}")
        print(f"📝 Message: {result['message']}")
        print(f"📊 Analysis: {result['analysis_data']['hod_detection_percentage']:.1f}% HOD detection rate")
        status_manager.update_detection_status(result)
    
    time.sleep(2)
    print("\n" + "="*60)
    
    # Test Scenario 2: HOD with visitors (should result in "busy")
    print("📹 Scenario 2: HOD with visitors (mostly 3 people, some fluctuation)")
    print("Expected result: present_and_busy")
    print("-" * 50)
    
    for i in range(120):  # 12 seconds of data
        # 75% of time HOD + 2 visitors, 15% HOD alone, 10% detection issues
        rand = random.random()
        if rand < 0.75:
            hod_present = True
            total_persons = 3  # HOD + 2 visitors
        elif rand < 0.90:
            hod_present = True
            total_persons = 1  # Sometimes visitors step out of frame
        else:
            # Detection issues
            hod_present = False
            total_persons = 2  # Only visitors detected
        
        status_manager.add_detection_frame(hod_present, total_persons)
        
        # Print analysis every 2 seconds
        if i % 20 == 19:
            buffer_info = status_manager.get_buffer_info()
            if isinstance(buffer_info, dict):
                print(f"  Frame {i+1:3d}: Buffer has {buffer_info['total_frames']} frames, "
                      f"HOD detected in {buffer_info['hod_percentage']:.1f}% of frames")
        
        time.sleep(0.1)
    
    # Analyze final result
    result = status_manager.analyze_stability_buffer()
    if result:
        print(f"\n✅ Final Result: {result['status']}")
        print(f"📝 Message: {result['message']}")
        print(f"📊 Analysis: {result['analysis_data']['hod_detection_percentage']:.1f}% HOD detection rate")
        status_manager.update_detection_status(result)
    
    time.sleep(2)
    print("\n" + "="*60)
    
    # Test Scenario 3: HOD not present (should result in "not_present")
    print("📹 Scenario 3: HOD not in office (occasional false detections)")
    print("Expected result: not_present")
    print("-" * 50)
    
    for i in range(120):  # 12 seconds of data
        # 85% of time no HOD, 15% false positive detections
        if random.random() < 0.85:
            hod_present = False
            total_persons = random.randint(0, 2)  # Sometimes other people
        else:
            # False positive HOD detection
            hod_present = True
            total_persons = random.randint(1, 2)
        
        status_manager.add_detection_frame(hod_present, total_persons)
        
        # Print analysis every 2 seconds
        if i % 20 == 19:
            buffer_info = status_manager.get_buffer_info()
            if isinstance(buffer_info, dict):
                print(f"  Frame {i+1:3d}: Buffer has {buffer_info['total_frames']} frames, "
                      f"HOD detected in {buffer_info['hod_percentage']:.1f}% of frames")
        
        time.sleep(0.1)
    
    # Analyze final result
    result = status_manager.analyze_stability_buffer()
    if result:
        print(f"\n✅ Final Result: {result['status']}")
        print(f"📝 Message: {result['message']}")
        print(f"📊 Analysis: {result['analysis_data']['hod_detection_percentage']:.1f}% HOD detection rate")
        status_manager.update_detection_status(result)
    
    print("\n" + "="*60)
    print("✅ Stability analysis test completed!")
    print("\n🔍 Key Benefits of 10-Second Stability Analysis:")
    print("• Eliminates flickering status changes")
    print("• Uses majority vote over 10-second window")
    print("• Handles temporary detection failures gracefully")
    print("• Provides reliable status determination")
    print("• Shows detection confidence percentage")
    
    print("\n🚀 To test with live camera:")
    print("1. Ensure correct httpx version: pip install 'httpx==0.24.1' 'httpcore==0.17.3'")
    print("2. Run detection: python run_live_detection_integrated.py")
    print("3. Run bot: python telegrambot_integrated.py")
    print("4. Send 'status' to your Telegram bot")
    print("5. Status updates every 10 seconds based on majority detection")

if __name__ == "__main__":
    simulate_realistic_detection()