@echo off
:: This runs the python script in the background without keeping the terminal open
start "" /B venv\Scripts\python.exe posture_gui.py
exit