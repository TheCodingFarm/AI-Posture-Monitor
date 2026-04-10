@echo off
echo =========================================
echo Setting up AI Posture Monitor...
echo =========================================

:: Create directories if needed
if not exist "venv" (
    echo [1/4] Creating Python Virtual Environment...
    python -m venv venv
) else (
    echo [1/4] Virtual Environment already exists.
)

echo [2/4] Downloading Alert Sound...
powershell -Command "Invoke-WebRequest -Uri 'https://assets.mixkit.co/active_storage/sfx/2866/2866.wav' -OutFile 'alert.wav'"

echo [3/4] Downloading MediaPipe Model...
powershell -Command "Invoke-WebRequest -Uri 'https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/latest/pose_landmarker_heavy.task' -OutFile 'pose_landmarker_heavy.task'"

echo [4/4] Installing Python Dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo =========================================
echo Done Installing! You can now run run.bat
echo =========================================
pause