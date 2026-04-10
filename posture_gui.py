import json
import os
import math # FIX 1: Added missing math import
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import subprocess
import cv2
import time
import numpy as np
import platform

CONFIG_FILE = "posture_config.json"
VideoCapDevice = 0
ALERT_SOUND = "alert.wav"
MODEL_PATH = 'pose_landmarker_heavy.task'
POSTURE_THRESHOLD = 0.15 
TIME_THRESHOLD = 3.0      

# Task Setup
BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Global for calibration
gaps = []

def process_calibration_result(result: vision.PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    global gaps
    if result.pose_landmarks:
        landmarks = result.pose_landmarks[0]
        vertical_gap = landmarks[11].y - landmarks[7].y
        shoulder_width = math.sqrt((landmarks[11].x - landmarks[12].x)**2 + 
                                    (landmarks[11].y - landmarks[12].y)**2)
        
        # Prevent division by zero if shoulders perfectly align (rare but possible)
        if shoulder_width > 0:
            ratio = vertical_gap / shoulder_width
            gaps.append(ratio)

def calibrate_posture():
    global gaps
    options = PoseLandmarkerOptions(
        base_options=BaseOptions(
            model_asset_path=MODEL_PATH,
            delegate=BaseOptions.Delegate.GPU 
        ),
        running_mode=VisionRunningMode.LIVE_STREAM,
        result_callback=process_calibration_result
    )
    print("Calibration starting... Sit straight!")
    gaps = []
    
    with PoseLandmarker.create_from_options(options) as landmarker:
        cap = cv2.VideoCapture(VideoCapDevice)
        start_time_ms = int(time.time() * 1000)
        try:
            # FIX 3: Wait until the async callbacks have populated 100 items
            while len(gaps) < 100:
                ret, frame = cap.read()
                if not ret: break
                
                current_time_ms = int(time.time() * 1000) - start_time_ms
                #frame = cv2.rotate(frame, cv2.ROTATE_180)
                #frame = cv2.flip(frame, 1)
                
                # UX Improvement: Show calibration progress
                cv2.putText(frame, f"Calibrating: {len(gaps)}/100", (10, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                cv2.imshow('AI Posture Monitor', frame)
                cv2.waitKey(1)
                
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
                landmarker.detect_async(mp_image, current_time_ms)
        finally:
            cap.release()
            cv2.destroyWindow('AI Posture Monitor') # Clean up calibration window
            
    avg_gap = np.mean(gaps)
    print(f"Calibration Complete. Baseline Ratio: {avg_gap:.4f}")
    return avg_gap * 0.8  # 20% tolerance

# State Management
class PostureState:
    def __init__(self):
        self.bad_posture_start = None
        self.is_notified = False
        self.current_status = "Good"
        self.last_beep_time = 0

state = PostureState()

def trigger_alert():
    if platform.system() == "Windows":
        import winsound
        winsound.PlaySound(sound_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
    else:
        subprocess.Popen(["paplay", ALERT_SOUND])
        subprocess.Popen(["notify-send", "Posture Alert", "Please sit up straight!", "--urgency=critical"])

def process_result(result: vision.PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    if result.pose_landmarks:
        landmarks = result.pose_landmarks[0]
        
        # FIX 2: Use the exact same math as calibration (Normalized Ratio)
        vertical_gap = landmarks[11].y - landmarks[7].y
        shoulder_width = math.sqrt((landmarks[11].x - landmarks[12].x)**2 + 
                                    (landmarks[11].y - landmarks[12].y)**2)
        
        if shoulder_width > 0:
            ratio = vertical_gap / shoulder_width

            if ratio < POSTURE_THRESHOLD:
                state.current_status = "Bad"
                if state.bad_posture_start is None:
                    state.bad_posture_start = time.time()
                
                elif (time.time() - state.bad_posture_start) > TIME_THRESHOLD:
                    if time.time() - state.last_beep_time > 5:
                        trigger_alert()
                        state.last_beep_time = time.time()
            else:
                state.current_status = "Good"
                state.bad_posture_start = None
                state.is_notified = False

# Initialization logic
if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            print(f"Loaded existing calibration: {config['threshold']:.4f}")
            POSTURE_THRESHOLD = config['threshold']
    except Exception as e:
        print(f"Error reading config: {e}. Recalibrating...")
        POSTURE_THRESHOLD = calibrate_posture()
        with open(CONFIG_FILE, 'w') as f:
            json.dump({"threshold": POSTURE_THRESHOLD}, f)
else:
    POSTURE_THRESHOLD = calibrate_posture()
    with open(CONFIG_FILE, 'w') as f:
        json.dump({"threshold": POSTURE_THRESHOLD}, f)

# Main Loop Setup
options = PoseLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path=MODEL_PATH,
        delegate=BaseOptions.Delegate.GPU 
    ),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=process_result
)

with PoseLandmarker.create_from_options(options) as landmarker:
    cap = cv2.VideoCapture(VideoCapDevice)
    start_time_ms = int(time.time() * 1000)
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            
            current_time_ms = int(time.time() * 1000) - start_time_ms
            #frame = cv2.rotate(frame, cv2.ROTATE_180)
            #frame = cv2.flip(frame, 1)
            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            landmarker.detect_async(mp_image, current_time_ms)

            color = (0, 255, 0) if state.current_status == "Good" else (0, 0, 255)
            cv2.putText(frame, f"Posture: {state.current_status}", (10, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            
            cv2.imshow('AI Posture Monitor', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()