# 🧍‍♂️ AI Posture Monitor

A lightweight, local, AI-powered posture monitor that uses your webcam to detect slouching. When bad posture is detected for a sustained period, the app provides a gentle audio or visual nudge to help you sit up straight.

Built using Python, OpenCV, and Google's MediaPipe Pose Landmarker.

---

## 🔒 Privacy First
**This application processes everything locally.** No video, images, or audio are ever recorded, saved, or transmitted to the cloud. The AI model runs entirely in your computer's RAM, ensuring complete privacy whether you are using this at home or in a shared workplace.

## ✨ Features
* **Two Operating Modes:**
  * **Background (Headless):** Runs invisibly in the background and only alerts you via a sound beep. Perfect for distraction-free work.
  * **GUI (Visual):** Opens a small webcam window showing your live posture status and AI skeletal tracking.
* **Cross-Platform:** Works on Windows and Ubuntu Linux.
* **Auto-Calibration:** Calibrates to your body proportions (shoulder width vs. neck gap) on first run, meaning it works no matter how far you sit from the camera.

---

## 🚀 Installation & Setup

This repository contains setup scripts that will automatically download the necessary AI models, audio files, and Python libraries. 

*(Note: The setup files are explicitly named with `win_` and `linux_` prefixes so you know exactly which one to click, even if your OS hides file extensions!)*

### For Windows Users
1. Clone or download this repository.
2. Double-click **`win_setup.bat`**. 
   * *This will open a terminal, download the AI model/audio, and create an isolated Python environment. It may take a minute or two.*
3. Once setup is complete, double-click **`win_run.bat`** to start the monitor in the background.

### For Ubuntu / Linux Users
1. Clone this repository and open a terminal in the folder.
2. Make the scripts executable:
   ```bash
   chmod +x linux_setup.sh linux_run.sh