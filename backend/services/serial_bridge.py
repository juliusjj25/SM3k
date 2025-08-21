import time
import serial
import requests
import json
from dotenv import load_dotenv
import os

"""
serial_bridge.py
-----------------
Reads JSON lines from a serial port and forwards them to the SmokerMaster3000
backend.  Environment variables control the serial port and baud rate as
well as the backend host and port.  The previous version incorrectly cast
BACKEND_HOST to an integer which prevented non‑numeric hostnames from being
used.  This version treats BACKEND_HOST as a string and ensures BAUD_RATE
is an integer.  Invalid JSON lines are silently skipped.
"""

load_dotenv()

SERIAL_PORT = os.getenv("SERIAL_PORT", "/dev/ttyACM0")
BAUD_RATE = int(os.getenv("BAUD_RATE", 115200))
BACKEND_HOST = os.getenv("BACKEND_HOST", "127.0.0.1")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", 5000))

# Retry loop for serial connection
while True:
    try:
        if os.path.exists(SERIAL_PORT):
            ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            print(f"Connected to {SERIAL_PORT}")
            break
        else:
            print(f"{SERIAL_PORT} not found. Retrying in 2s...")
    except Exception as e:
        print("Error opening serial port:", e)
    time.sleep(2)

# Main loop: read, parse JSON, forward to backend
while True:
    try:
        line = ser.readline().decode('utf-8', errors='replace').strip()
        if line:
            try:
                data = json.loads(line)
                url = f'http://{BACKEND_HOST}:{BACKEND_PORT}/log-entry'
                requests.post(url, json=data)
            except json.JSONDecodeError:
                # Skip invalid JSON lines
                print("Invalid JSON received, skipping line.")
            except Exception as e:
                print("Error sending data:", e)
    except Exception as e:
        print("Error reading from serial:", e)
        time.sleep(1)
