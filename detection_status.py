# detection_status.py
"""
Shared status management for HOD detection system and Telegram bot
"""
import json
import os
import time
from datetime import datetime, timedelta
from collections import Counter

class DetectionStatusManager:
    def __init__(self, status_file_path="hod_detection_status.json"):
        self.status_file_path = status_file_path
        self.last_update_timeout = 30  # seconds - consider offline if no update in 30 sec
        
        # Stability buffer for 10-second analysis
        self.stability_buffer = []
        self.buffer_duration = 10  # seconds
        self.max_buffer_size = 300  # Maximum entries (30fps * 10sec = 300 frames)
    
    def add_detection_frame(self, hod_present, total_persons):
        """
        Add a single frame detection result to the stability buffer
        
        Args:
            hod_present (bool): Whether HOD is detected in this frame
            total_persons (int): Total number of persons detected in this frame
        """
        current_time = time.time()
        
        # Add current detection to buffer
        frame_data = {
            'timestamp': current_time,
            'hod_present': hod_present,
            'total_persons': total_persons,
            'other_persons': total_persons - (1 if hod_present else 0)
        }
        
        self.stability_buffer.append(frame_data)
        
        # Remove entries older than buffer_duration
        cutoff_time = current_time - self.buffer_duration
        self.stability_buffer = [
            frame for frame in self.stability_buffer 
            if frame['timestamp'] >= cutoff_time
        ]
        
        # Limit buffer size to prevent memory issues
        if len(self.stability_buffer) > self.max_buffer_size:
            self.stability_buffer = self.stability_buffer[-self.max_buffer_size:]
    
    def analyze_stability_buffer(self):
        """
        Analyze the last 10 seconds of detection data and determine stable status
        
        Returns:
            dict: Analyzed status based on majority vote over 10 seconds
        """
        if not self.stability_buffer:
            return None
        
        # Count HOD presence over the buffer period
        hod_present_count = sum(1 for frame in self.stability_buffer if frame['hod_present'])
        total_frames = len(self.stability_buffer)
        
        # Majority vote: HOD is considered present if detected in >50% of frames
        hod_stable_present = hod_present_count > (total_frames * 0.5)
        
        if hod_stable_present:
            # HOD is present - now determine if busy or free
            # Get person counts only when HOD was present
            hod_present_frames = [frame for frame in self.stability_buffer if frame['hod_present']]
            
            if hod_present_frames:
                # Calculate average other persons when HOD is present
                total_other_persons = sum(frame['other_persons'] for frame in hod_present_frames)
                avg_other_persons = total_other_persons / len(hod_present_frames)
                
                # If average other persons > 0.5, consider HOD as busy
                if avg_other_persons > 0.5:
                    status = "present_and_busy"
                    message = f"Currently busy - average {avg_other_persons:.1f} other person(s) present"
                else:
                    status = "present_and_free"
                    message = "Available for meetings and consultations"
                
                # Use the most recent total_persons for display
                recent_total = hod_present_frames[-1]['total_persons']
                recent_others = hod_present_frames[-1]['other_persons']
            else:
                # Fallback (shouldn't happen)
                status = "present_and_free"
                message = "Available for meetings and consultations"
                recent_total = 1
                recent_others = 0
        else:
            # HOD not present in majority of frames
            status = "not_present"
            message = "Not available in cabin"
            
            # Use average of all frames for total persons
            avg_total_persons = sum(frame['total_persons'] for frame in self.stability_buffer) / total_frames
            recent_total = int(avg_total_persons)
            recent_others = recent_total
        
        return {
            'hod_present': hod_stable_present,
            'total_persons': recent_total,
            'other_persons': recent_others,
            'status': status,
            'message': message,
            'analysis_data': {
                'frames_analyzed': total_frames,
                'hod_detected_frames': hod_present_count,
                'hod_detection_percentage': (hod_present_count / total_frames) * 100,
                'buffer_duration_actual': self.stability_buffer[-1]['timestamp'] - self.stability_buffer[0]['timestamp'] if len(self.stability_buffer) > 1 else 0
            }
        }
    
    def update_detection_status(self, analysis_result=None):
        """
        Update the detection status file with analyzed results
        
        Args:
            analysis_result (dict): Result from analyze_stability_buffer() or None to analyze current buffer
        """
        if analysis_result is None:
            analysis_result = self.analyze_stability_buffer()
        
        if analysis_result is None:
            print("No detection data available for analysis")
            return False
        
        status_data = {
            "hod_present": analysis_result['hod_present'],
            "total_persons": analysis_result['total_persons'],
            "other_persons": analysis_result['other_persons'],
            "status": analysis_result['status'],
            "message": analysis_result['message'],
            "timestamp": datetime.now().isoformat(),
            "last_update": time.time(),
            "stability_analysis": analysis_result['analysis_data']
        }
        
        try:
            with open(self.status_file_path, 'w') as f:
                json.dump(status_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving detection status: {e}")
            return False
    
    def get_current_status(self):
        """
        Get the current detection status for the Telegram bot
        
        Returns:
            dict: Status information or None if file doesn't exist/is outdated
        """
        try:
            if not os.path.exists(self.status_file_path):
                return None
                
            with open(self.status_file_path, 'r') as f:
                status_data = json.load(f)
            
            # Check if status is recent (within timeout period)
            last_update = status_data.get("last_update", 0)
            if time.time() - last_update > self.last_update_timeout:
                # Status is outdated - detection system might be offline
                return {
                    "status": "system_offline",
                    "message": "Detection system is offline",
                    "timestamp": datetime.now().isoformat(),
                    "hod_present": False,
                    "total_persons": 0,
                    "other_persons": 0
                }
            
            return status_data
            
        except Exception as e:
            print(f"Error reading detection status: {e}")
            return None
    
    def is_detection_system_active(self):
        """Check if the detection system is actively updating status"""
        status = self.get_current_status()
        return status is not None and status.get("status") != "system_offline"
    
    def get_buffer_info(self):
        """Get information about the current stability buffer"""
        if not self.stability_buffer:
            return "Buffer is empty"
        
        current_time = time.time()
        buffer_span = current_time - self.stability_buffer[0]['timestamp']
        hod_count = sum(1 for frame in self.stability_buffer if frame['hod_present'])
        
        return {
            'total_frames': len(self.stability_buffer),
            'buffer_duration': buffer_span,
            'hod_detected_frames': hod_count,
            'hod_percentage': (hod_count / len(self.stability_buffer)) * 100 if self.stability_buffer else 0,
            'ready_for_analysis': buffer_span >= self.buffer_duration
        }