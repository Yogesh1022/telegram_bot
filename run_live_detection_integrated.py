# run_live_detection_integrated.py

import cv2
import numpy as np
import face_recognition
import pickle
import time
from detection_status import DetectionStatusManager

# --- CONFIGURATION ---
YOLO_MODEL_PATH = 'yolov5n.onnx'
HOD_ENCODING_PATH = 'hod_encoding.pickle'
CONF_THRESHOLD = 0.5
NMS_THRESHOLD = 0.4 # Non-Maximum Suppression

# Initialize status manager for Telegram bot integration
status_manager = DetectionStatusManager()

# --- INITIALIZATION ---
print("[INFO] Loading models and starting camera...")

# Load YOLOv5 model using OpenCV's DNN module
try:
    net = cv2.dnn.readNet(YOLO_MODEL_PATH)
    print("[INFO] YOLO model loaded successfully")
except Exception as e:
    print(f"[ERROR] Failed to load YOLO model: {e}")
    exit(1)

# Load the HOD's high-precision facial signature
try:
    with open(HOD_ENCODING_PATH, "rb") as f:
        hod_data = pickle.load(f)
    print("[INFO] HOD encoding loaded successfully")
except Exception as e:
    print(f"[ERROR] Failed to load HOD encoding: {e}")
    exit(1)

# Initialize camera
print("[INFO] Camera starting...")
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("[ERROR] Could not open camera")
    exit(1)

# Allow the camera sensor to warm up
time.sleep(2.0)

# Frame counter for status updates
frame_count = 0
analysis_interval = 300  # Analyze every 300 frames (≈10 seconds at 30fps)
last_analysis_time = time.time()

print("[INFO] Starting live detection loop with 10-second stability analysis...")
print("[INFO] Status will be updated every 10 seconds based on majority detection")
print("[INFO] Press 'q' to quit")

# --- LIVE DETECTION LOOP ---
while True:
    ret, frame = cap.read()
    if not ret:
        print("[ERROR] Failed to grab frame from camera.")
        break

    frame_height, frame_width = frame.shape[:2]
    
    # Prepare the frame for the YOLO model
    # The model expects a 640x640 image
    blob = cv2.dnn.blobFromImage(frame, 1/255.0, (640, 640), swapRB=True, crop=False)
    net.setInput(blob)
    outputs = net.forward()

    # --- Process YOLO Output (Corrected Method) ---
    boxes = []
    confidences = []

    rows = outputs[0].shape[0]
    for i in range(rows):
        row = outputs[0][i]
        confidence = row[4] # Overall confidence of the detection
        
        if confidence > CONF_THRESHOLD:
            scores = row[5:] # Scores for all 80 classes
            class_id = np.argmax(scores)
            
            # Check if the detected object is a 'person' (class ID 0 in COCO dataset)
            if class_id == 0:
                # Extract bounding box coordinates and scale them to the original frame size
                x, y, w, h = row[0].item(), row[1].item(), row[2].item(), row[3].item() 
                left = int((x - 0.5 * w) * (frame_width / 640.0))
                top = int((y - 0.5 * h) * (frame_height / 640.0))
                width = int(w * (frame_width / 640.0))
                height = int(h * (frame_height / 640.0))
                
                boxes.append([left, top, width, height])
                confidences.append(float(confidence))

    # Apply Non-Maximum Suppression to remove redundant, overlapping boxes
    indices = cv2.dnn.NMSBoxes(boxes, confidences, CONF_THRESHOLD, NMS_THRESHOLD)
    
    person_count = len(indices) if len(indices) > 0 else 0
    hod_found_in_frame = False
    
    if person_count > 0:
        for i in indices.flatten():
            x, y, w, h = boxes[i]
            
            label = "Person"
            color = (0, 255, 0) # Green for Person

            # Targeted HOD Recognition
            if not hod_found_in_frame:
                # Define the region of interest (ROI) for the detected person
                top_roi, left_roi = max(0, y), max(0, x)
                bottom_roi, right_roi = min(frame_height, y + h), min(frame_width, x + w)
                
                person_roi_rgb = cv2.cvtColor(frame[top_roi:bottom_roi, left_roi:right_roi], cv2.COLOR_BGR2RGB)
                
                # Use the fast 'hog' model for real-time performance on the Pi
                face_locations = face_recognition.face_locations(person_roi_rgb, model='hog')
                
                if face_locations:
                    face_encodings = face_recognition.face_encodings(person_roi_rgb, face_locations)
                    if face_encodings:  # Ensure face encoding was successful
                        # Compare face against the high-quality HOD signature
                        matches = face_recognition.compare_faces(hod_data["encodings"], face_encodings[0], tolerance=0.55)
                        if True in matches:
                            label = "HOD"
                            color = (0, 0, 255) # Red for HOD
                            hod_found_in_frame = True
            
            # Draw the bounding box and label on the frame
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    # Add current frame detection to stability buffer
    status_manager.add_detection_frame(hod_found_in_frame, person_count)
    
    # Update status every 10 seconds based on stability analysis
    frame_count += 1
    current_time = time.time()
    
    # Perform analysis every 10 seconds
    if current_time - last_analysis_time >= 10.0:
        try:
            # Analyze the stability buffer and update status
            analysis_result = status_manager.analyze_stability_buffer()
            if analysis_result:
                status_manager.update_detection_status(analysis_result)
                
                stability_info = analysis_result['analysis_data']
                print(f"[STABILITY ANALYSIS] {stability_info['frames_analyzed']} frames analyzed over {stability_info['buffer_duration_actual']:.1f}s")
                print(f"[ANALYSIS RESULT] HOD detected in {stability_info['hod_detection_percentage']:.1f}% of frames")
                print(f"[FINAL STATUS] {analysis_result['status']} - {analysis_result['message']}")
                
        except Exception as e:
            print(f"[ERROR] Failed to perform stability analysis: {e}")
        
        last_analysis_time = current_time
    
    # Display buffer info every 60 frames for monitoring
    if frame_count % 60 == 0:
        buffer_info = status_manager.get_buffer_info()
        if isinstance(buffer_info, dict):
            print(f"[BUFFER INFO] {buffer_info['total_frames']} frames, {buffer_info['buffer_duration']:.1f}s, HOD: {buffer_info['hod_percentage']:.1f}%")

    # Determine current frame status for display
    if hod_found_in_frame:
        other_persons = person_count - 1
        if other_persons == 0:
            frame_status_display = "HOD Present - FREE"
            frame_status_color = (0, 255, 0)  # Green
        else:
            frame_status_display = f"HOD Present - BUSY ({other_persons} others)"
            frame_status_color = (0, 165, 255)  # Orange
    else:
        frame_status_display = "HOD Not Present"
        frame_status_color = (0, 0, 255)  # Red

    # Get stable status from last analysis
    stable_status = status_manager.get_current_status()
    if stable_status and stable_status.get('status') != 'system_offline':
        stable_display = f"Stable: {stable_status['status'].replace('_', ' ').title()}"
        if stable_status['status'] == 'present_and_free':
            stable_color = (0, 255, 0)  # Green
        elif stable_status['status'] == 'present_and_busy':
            stable_color = (0, 165, 255)  # Orange
        else:
            stable_color = (0, 0, 255)  # Red
    else:
        stable_display = "Stable: Analyzing..."
        stable_color = (128, 128, 128)  # Gray

    # Display current frame status
    frame_text = f"Current: {frame_status_display} | Total: {person_count}"
    cv2.putText(frame, frame_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, frame_status_color, 2)
    
    # Display stable status
    stable_text = f"{stable_display}"
    cv2.putText(frame, stable_text, (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, stable_color, 2)
    
    # Display buffer info
    buffer_info = status_manager.get_buffer_info()
    if isinstance(buffer_info, dict):
        buffer_text = f"Buffer: {buffer_info['total_frames']} frames ({buffer_info['hod_percentage']:.0f}% HOD)"
        cv2.putText(frame, buffer_text, (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Show the final frame
    cv2.imshow("Live HOD Detection - Integrated", frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) == ord('q'):
        break

# --- Cleanup ---
print("[INFO] Closing application...")
cap.release()
cv2.destroyAllWindows()
print("[INFO] Application closed successfully")