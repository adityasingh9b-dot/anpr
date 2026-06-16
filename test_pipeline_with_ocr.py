import cv2
import torch
import numpy as np
from ultralytics import YOLO
import easyocr
import time
import difflib
import re
from collections import Counter
from database import db_manager

import sys
import os
# Force Python to look in current directory first
sys.path.insert(0, os.getcwd())

import cpp_ingestion # Ab ise load hona hi padega!

# Current directory ko path mein add karo
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import cpp_ingestion
    print("✅ C++ Module loaded successfully!")
except ImportError:
    print("❌ Error: C++ shared object (.so) still not found!")
    # Debug ke liye path print karo
    print(f"Python path: {sys.path}")
    exit(1)

try:
    import cpp_ingestion
except ImportError:
    print("❌ Error: C++ shared object (.so) nahi mila!")
    exit(1)

# --- GLOBAL PERSISTENCE STORAGE ---
last_detected_plate = None
last_detection_time = 0
last_bbox = None
is_plate_active = False 

def apply_indian_anpr_heuristics(text):
    # 1. Clean noise: Sirf alphanumeric rakho
    cleaned = "".join([c for c in text if c.isalnum()]).upper().strip()
    
    # 2. Length check: Indian plates kam se kam 8-10 chars ki hoti hain
    if len(cleaned) < 8 or len(cleaned) > 13: return None
    
    char_list = list(cleaned)
    
    # 3. Position-based Correction
    for i, char in enumerate(char_list):
        # Indices 0, 1: State Code (Must be Alphabets)
        if i in [0, 1]:
            if char.isdigit():
                # Common confusion fixes
                mapping = {'0': 'D', '1': 'I', '4': 'A', '8': 'B'}
                char_list[i] = mapping.get(char, char)
        
        # Indices 2, 3: District Code (Must be Digits)
        elif i in [2, 3]:
            if not char.isdigit():
                # Common confusion fixes
                mapping = {'O': '0', 'I': '1', 'Z': '2', 'A': '4', 'S': '5', 'B': '8', 'G': '6'}
                char_list[i] = mapping.get(char, char)
        
        # Series & Number part (General fix for O -> 0)
        elif char == 'O': 
            char_list[i] = '0'
            
    corrected = "".join(char_list)
    
    # 4. Strict Regex Validation
    # Format: [2 Alphabets][2 Digits][1-3 Alphanumeric][4 Digits]
    # Example: DL07CQ1939 or HR26FC2782
    pattern = r"^[A-Z]{2}[0-9]{2}[A-Z0-9]{1,3}[0-9]{4}$"
    
    if re.match(pattern, corrected):
        return corrected
    
    return None

def main():
    global last_detected_plate, last_detection_time, last_bbox, is_plate_active
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    plate_model = YOLO('/home/aditya/Desktop/anpr/runs/detect/train-6/weights/best.pt').to(device)
    ocr_reader = easyocr.Reader(['en'], gpu=torch.cuda.is_available())
    
    # Stabilization Buffer
    detection_buffer = []
    
    if not cpp_ingestion.initialize_camera(): return

    print("🚀 Stabilized & Strict ANPR Engine Active...")
    
    # Initialize outside loop
    last_db_status = "Searching..."
    
    while True:
        start_time = time.time()
        frame = cpp_ingestion.get_processed_frame()
        
        # Default status for this frame
        current_display_status = last_db_status if last_db_status else "Searching..."
        
        if frame is None or frame.size == 0: continue
        
        # YOLO inference
        results = plate_model(frame, verbose=False)
        detected_this_frame = None
        
        for result in results:
            for box in result.boxes.xyxy.cpu().numpy():
                x1, y1, x2, y2 = map(int, box[:4])
                if (x2 - x1) < 50 or (y2 - y1) < 20: continue
                
                plate_crop = frame[y1:y2, x1:x2]
                gray_crop = cv2.cvtColor(plate_crop, cv2.COLOR_BGR2GRAY)
                proc = cv2.adaptiveThreshold(gray_crop, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
                ocr = ocr_reader.readtext(proc, allowlist='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
                
                for (_, raw, prob) in ocr:
                    if prob > 0.45:
                        no = apply_indian_anpr_heuristics(raw)
                        if no:
                            detected_this_frame = (no, (x1, y1, x2, y2))
                            break
                if detected_this_frame: break

        # --- SMART TRACKING & VOTING LOGIC ---
        if detected_this_frame:
            no, (x1, y1, x2, y2) = detected_this_frame
            detection_buffer.append(no)
            if len(detection_buffer) > 20: detection_buffer.pop(0) 
            
            most_common, count = Counter(detection_buffer).most_common(1)[0]
            
            if count >= 12:
                if most_common != last_detected_plate:
                    from database import db_manager
                    db_response = db_manager.check_vehicle_status(most_common)
                    status = db_response['status'] 
                    
                    db_manager.log_pass(most_common, status)
                    print(f"🎯 [CONFIRMED ENTRY]: {most_common} | Status: {status} | LOGGED TO DB")
                    
                    last_detected_plate = most_common
                    last_db_status = status  # Update global status
                    detection_buffer = [] 
            
            last_detection_time = time.time()
            last_bbox = (x1, y1, x2, y2)
            is_plate_active = True
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
            # Use most_common and current status
            cv2.putText(frame, f"PLATE: {most_common} | {last_db_status}", (x1, y1 - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        else:
            if is_plate_active and (time.time() - last_detection_time) > 2.0:
                is_plate_active = False
                last_detected_plate = None
                last_db_status = "Searching..."
            elif last_bbox and is_plate_active:
                cv2.rectangle(frame, (last_bbox[0], last_bbox[1]), (last_bbox[2], last_bbox[3]), (0, 255, 255), 2)
                cv2.putText(frame, f"LAST: {last_detected_plate}", (last_bbox[0], last_bbox[1] - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        # Performance Display
        fps = 1.0 / (time.time() - start_time)
        cv2.putText(frame, f"FPS: {fps:.2f}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.imshow("Low-Latency Indian ANPR Pipeline", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cv2.destroyAllWindows()
    
    
    
if __name__ == "__main__":
    main()
