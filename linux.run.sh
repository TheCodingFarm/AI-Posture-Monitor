#!/bin/bash

# Navigate to the script directory
cd "$(dirname "$0")"

# Activate environment and run
echo "Starting Posture Monitor..."
source venv/bin/activate
python3 posture_gui.py