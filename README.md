# 🧍‍♂️ AI Posture Monitor by TheCodingFarm

A lightweight, local, AI-powered posture monitor that uses your webcam to detect slouching. When bad posture is detected for a sustained period, the app provides a gentle audio or visual nudge to help you sit up straight.

This application is an open-source freeware product developed by **TheCodingFarm**, showcasing our commitment to practical AI product development. We specialize in building and customizing AI tools for organizations seeking tailored technical solutions.

---

## 🔒 Privacy First
**This application processes everything locally.** No video, images, or audio are ever recorded, saved, or transmitted to the cloud. The AI model runs entirely in your computer's RAM, ensuring complete privacy whether you are using this at home or in a shared workplace.

## ✨ Features
* **Two Operating Modes:**
  * **Background (Headless):** Runs invisibly in the background and only alerts you via a sound beep. Perfect for distraction-free work or setting up as a startup service.
  * **GUI (Visual):** Opens a small webcam window showing your live posture status and AI skeletal tracking.
* **Cross-Platform:** Works on Windows and Linux.
* **Automated Setup:** Single-click scripts to handle virtual environments, library installations, and asset downloading.

---

## 🚀 Installation & Setup

This repository contains setup scripts that will automatically create a Python virtual environment (`venv`), install dependencies from `requirements.txt`, and download the necessary AI models (MediaPipe Pose Landmarker) and audio files (Mixkit).

### For Windows Users
1. Clone or download this repository.
2. Double-click **`win_setup.bat`**. 
   * *This will open a terminal, download the AI model/audio, and create an isolated Python environment. It may take a minute or two.*
3. Once setup is complete, double-click **`win_run.bat`** to start the monitor.
   * **Note:** The Windows run script defaults to the **Headless** mode (`posture_headless.py`). This allows you to add `win_run.bat` to your Windows Startup folder so the posture monitor acts like a background service every time you reboot.
   * *If you want to view the visual tracker, you can manually run `posture_gui.py` using the Python executable inside the newly created `venv` folder.*

### For Linux Users
1. Clone this repository and open a terminal in the folder.
2. Make the scripts executable:
   ```bash
   chmod +x linux_setup.sh linux_run.sh
   ```
3. Run the setup script:
   ```bash
   ./linux_setup.sh
   ```
4. Start the application:
   ```bash
   ./linux_run.sh
   ```
   * **Note:** The Linux run script defaults to the **GUI** mode (`posture_gui.py`).

---

## 📂 Repository Structure
To keep the beta release clean, this repository only tracks the absolute essentials:

* `posture_gui.py` - The visual interface for posture monitoring.
* `posture_headless.py` - The background-only version for distraction-free monitoring.
* `requirements.txt` - Python dependencies (OpenCV, MediaPipe, Tkinter, etc.).
* `linux_setup.sh` / `linux_run.sh` - Bash utilities for Linux environments.
* `win_setup.bat` / `win_run.bat` - Batch utilities for Windows environments.
* `.gitignore` & `README.md`

*(Note: The heavy AI model `.task` file and the `.wav` audio files are intentionally excluded from the repository to save bandwidth and respect origin licensing. They are downloaded directly to your machine when you run the setup scripts).*

---

## ⚖️ Legal & Attributions

This project utilizes incredible free resources from the developer community. 

* **Google MediaPipe:** The pose tracking is powered by Google's MediaPipe framework. The `pose_landmarker_heavy.task` model is downloaded directly from Google's servers during setup.
* **Mixkit Audio:** The alert sound used in this project is downloaded dynamically from Mixkit. The audio file is not distributed directly within this repository. By using this software, you acknowledge that the audio file is subject to the [Mixkit User Terms](https://mixkit.co/terms/) and you only receive a non-exclusive license to use the item, acquiring no ownership rights.

## 🏢 About TheCodingFarm
**TheCodingFarm** focuses on innovative AI Product Development. This Posture Monitor is provided as free, open-source software to demonstrate our capabilities in integrating machine learning models into everyday utility applications. If your organization requires customized AI tools, automation pipelines, or bespoke technical development, TheCodingFarm is ready to build it.