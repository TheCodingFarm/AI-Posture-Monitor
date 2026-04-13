import json
import os
import math
import threading
import time
import platform
import subprocess
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image, ImageTk

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for Nuitka onefile """
    # Nuitka stores the path to the extracted files in the directory of the script
    base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)

# Updated Configuration using the helper
CONFIG_FILE = "posture_config.json"
MODEL_PATH = get_resource_path('pose_landmarker_heavy.task')
ALERT_SOUND = get_resource_path('alert.wav')
VIDEO_DEVICE = 0

# MediaPipe Setup
BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

class PostureApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AI Posture Monitor")
        self.geometry("900x650")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # State
        self.threshold = 0.15
        self.time_threshold = 3.0
        self.rotation = 0
        self.flip_horizontal = True
        self.device_index = 0
        self.is_running = False
        self.is_calibrating = False
        self.calibration_gaps = []
        self.current_status = "Initializing..."
        self.bad_posture_start = None
        self.last_alert_time = 0
        self.cap = None
        self.landmarker = None

        self.load_config()
        self.setup_ui()
        self.start_engine()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    self.threshold = config.get('threshold', 0.15)
                    self.rotation = config.get('rotation', 0)
                    self.flip_horizontal = config.get('flip_horizontal', True)
                    self.device_index = config.get('device_index', 0)
            except:
                pass

    def save_config(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump({
                "threshold": self.threshold,
                "rotation": self.rotation,
                "flip_horizontal": self.flip_horizontal,
                "device_index": self.device_index
            }, f)

    def setup_ui(self):
        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.logo_label = ctk.CTkLabel(self.sidebar, text="Posture AI", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.pack(pady=20)

        self.status_label = ctk.CTkLabel(self.sidebar, text=f"Status: {self.current_status}", text_color="gray")
        self.status_label.pack(pady=10)

        self.calibrate_btn = ctk.CTkButton(self.sidebar, text="Calibrate", command=self.start_calibration)
        self.calibrate_btn.pack(pady=10, padx=20)

        # Camera Controls
        self.camera_label = ctk.CTkLabel(self.sidebar, text="Camera Settings", font=ctk.CTkFont(size=12, weight="bold"))
        self.camera_label.pack(pady=(20, 5))

        self.rotate_btn = ctk.CTkButton(self.sidebar, text="Rotate 90°", command=self.rotate_camera, fg_color="transparent", border_width=1)
        self.rotate_btn.pack(pady=5, padx=20)

        self.flip_btn = ctk.CTkButton(self.sidebar, text="Flip Horizontal", command=self.toggle_flip, fg_color="transparent", border_width=1)
        self.flip_btn.pack(pady=5, padx=20)

        self.device_label = ctk.CTkLabel(self.sidebar, text="Select Camera", font=ctk.CTkFont(size=12))
        self.device_label.pack(pady=(10, 0))

        self.available_cameras = self.find_cameras()
        camera_options = [f"Camera {i}" for i in self.available_cameras] if self.available_cameras else ["No Camera Found"]

        self.device_menu = ctk.CTkOptionMenu(self.sidebar, values=camera_options, command=self.change_camera)
        if self.available_cameras:
            current_selection = f"Camera {self.device_index}"
            if current_selection in camera_options:
                self.device_menu.set(current_selection)
            else:
                self.device_menu.set(camera_options[0])
                self.device_index = self.available_cameras[0]
        else:
            self.device_menu.set("No Camera Found")
            self.device_menu.configure(state="disabled")

        self.device_menu.pack(pady=5, padx=20)

        # Sensitivity Slider
        self.slider_label = ctk.CTkLabel(self.sidebar, text="Sensitivity Threshold")
        self.slider_label.pack(pady=(20, 0))

        self.threshold_slider = ctk.CTkSlider(self.sidebar, from_=0.05, to=0.4, number_of_steps=100, command=self.update_threshold)
        self.threshold_slider.set(self.threshold)
        self.threshold_slider.pack(pady=10, padx=20)

        self.threshold_val_label = ctk.CTkLabel(self.sidebar, text=f"{self.threshold:.3f}")
        self.threshold_val_label.pack()

        # Main View
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.video_label = ctk.CTkLabel(self.main_frame, text="")
        self.video_label.pack(expand=True, fill="both")

    def find_cameras(self):
        cameras = []
        for i in range(5): # Check first 5 indices
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    cameras.append(i)
                cap.release()
        return cameras

    def change_camera(self, choice):
        if choice == "No Camera Found":
            return

        new_index = int(choice.split(" ")[1])
        if new_index != self.device_index:
            self.device_index = new_index
            self.save_config()
            # The video loop will pick up the change automatically if we restart the capture
            self.restart_capture = True

    def rotate_camera(self):
        self.rotation = (self.rotation + 90) % 360
        self.save_config()

    def toggle_flip(self):
        self.flip_horizontal = not self.flip_horizontal
        self.save_config()

    def update_threshold(self, val):
        self.threshold = float(val)
        self.threshold_val_label.configure(text=f"{self.threshold:.3f}")
        self.save_config()

    def start_calibration(self):
        self.is_calibrating = True
        self.calibration_gaps = []
        self.calibrate_btn.configure(state="disabled", text="Calibrating...")

    def trigger_alert(self):
        if platform.system() == "Windows":
            import winsound
            winsound.PlaySound(ALERT_SOUND, winsound.SND_FILENAME | winsound.SND_ASYNC)
            try:
                from win11toast import toast
                toast('Posture Alert', 'Please sit up straight!', duration='short')
            except:
                pass
        else:
            # Linux/Mac fallbacks
            try:
                subprocess.Popen(["paplay", ALERT_SOUND])
                subprocess.Popen(["notify-send", "Posture Alert", "Please sit up straight!"])
            except:
                pass

    def process_result(self, result: vision.PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
        if not result.pose_landmarks:
            self.current_status = "No Person Detected"
            return

        landmarks = result.pose_landmarks[0]
        # Calculate ratio: (Shoulder to Ear vertical distance) / (Shoulder Width)
        # Ear is index 7 (left) or 8 (right). Shoulder is 11 (left) or 12 (right).
        # We use left side (7 and 11) for simplicity or average.

        vertical_gap = landmarks[11].y - landmarks[7].y
        shoulder_width = math.sqrt((landmarks[11].x - landmarks[12].x)**2 +
                                    (landmarks[11].y - landmarks[12].y)**2)

        if shoulder_width > 0:
            ratio = vertical_gap / shoulder_width

            if self.is_calibrating:
                self.calibration_gaps.append(ratio)
                if len(self.calibration_gaps) >= 50:
                    avg_gap = np.mean(self.calibration_gaps)
                    self.threshold = avg_gap * 0.85 # 15% tolerance
                    self.after(0, lambda: self.threshold_slider.set(self.threshold))
                    self.after(0, lambda: self.threshold_val_label.configure(text=f"{self.threshold:.3f}"))
                    self.is_calibrating = False
                    self.after(0, lambda: self.calibrate_btn.configure(state="normal", text="Calibrate"))
                    self.save_config()

            # Posture Logic
            if ratio < self.threshold:
                self.current_status = "Bad Posture"
                if self.bad_posture_start is None:
                    self.bad_posture_start = time.time()
                elif (time.time() - self.bad_posture_start) > self.time_threshold:
                    if time.time() - self.last_alert_time > 10: # Alert every 10s
                        self.trigger_alert()
                        self.last_alert_time = time.time()
            else:
                self.current_status = "Good Posture"
                self.bad_posture_start = None

    def start_engine(self):
        self.is_running = True
        threading.Thread(target=self.video_loop, daemon=True).start()

    def video_loop(self):
      try:
        options = PoseLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=MODEL_PATH),
            running_mode=VisionRunningMode.LIVE_STREAM,
            result_callback=self.process_result
        )

        with PoseLandmarker.create_from_options(options) as landmarker:
            while self.is_running:
                # Open camera once per "session"
                self.cap = cv2.VideoCapture(self.device_index, cv2.CAP_DSHOW)
                self.restart_capture = False
                start_time_ms = int(time.time() * 1000)

                while self.is_running and self.cap.isOpened() and not self.restart_capture:
                    ret, frame = self.cap.read()
                    if not ret:
                        time.sleep(0.1)
                        continue

                    # Transformations (Rotation/Flip)
                    if self.rotation != 0:
                        mode = {90: cv2.ROTATE_90_CLOCKWISE, 180: cv2.ROTATE_180, 270: cv2.ROTATE_90_COUNTERCLOCKWISE}
                        frame = cv2.rotate(frame, mode[self.rotation])
                    if self.flip_horizontal:
                        frame = cv2.flip(frame, 1)

                    # Feed MediaPipe
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
                    timestamp = int(time.time() * 1000) - start_time_ms
                    landmarker.detect_async(mp_image, timestamp)

                    # Draw status on the frame for the user to see
                    color = (0, 255, 0) if "Good" in self.current_status else (0, 0, 255)
                    cv2.putText(frame, self.current_status, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

                    # Convert to Tkinter Image
                    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    img_tk = ImageTk.PhotoImage(image=img)

                    # Final UI update with garbage collection fix
                    self.after(0, self._update_display, img_tk)

                    time.sleep(0.01)

                self.cap.release()
      except Exception as e:
        self.current_status = "Engine Error"
        print(f"CRITICAL ERROR: {e}")
        error_msg = f"Failed to start AI Engine: {e}" 
        self.after(0, lambda: messagebox.showerror("Hardware Error", error_msg))
    
    def _update_display(self, img_tk):
        self.video_label.configure(image=img_tk)
        self.video_label._image_ref = img_tk  # Keep reference alive!
        self.status_label.configure(
            text=f"Status: {self.current_status}",
            text_color="green" if "Good" in self.current_status else "red"
        )

    def on_closing(self):
        self.is_running = False
        if self.cap: self.cap.release()
        self.destroy()

if __name__ == "__main__":
    if not os.path.exists(MODEL_PATH):
        print(f"Error: {MODEL_PATH} not found. Please download it from MediaPipe.")

    app = PostureApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
