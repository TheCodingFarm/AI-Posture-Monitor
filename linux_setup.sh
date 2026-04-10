#!/bin/bash

echo "------------------------------------------------"
echo "Initializing AI Posture Monitor Setup (Ubuntu)"
echo "------------------------------------------------"

# 1. Install System Dependencies
echo "[1/5] Installing system dependencies (sudo required)..."
sudo apt update
sudo apt install -y python3-venv python3-pip wget libnotify-bin pulseaudio-utils libgl1

# 2. Create Virtual Environment
echo "[2/5] Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 3. Install Python Packages
echo "[3/5] Installing Python libraries..."
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    pip install mediapipe opencv-python numpy
fi

# 4. Download Resource Files
echo "[4/5] Downloading MediaPipe model (approx. 34MB)..."
wget -O pose_landmarker_heavy.task "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/latest/pose_landmarker_heavy.task"

echo "[5/5] Downloading alert sound..."
wget -O alert.wav "https://assets.mixkit.co/active_storage/sfx/2866/2866.wav"

echo "------------------------------------------------"
echo "Setup Complete! Use ./run.sh to start."
echo "------------------------------------------------"