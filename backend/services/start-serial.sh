#!/bin/bash

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Run the serial bridge
exec python3 serial_bridge.py
