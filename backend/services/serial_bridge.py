import time
import serial
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

SERIAL_PORT = os.getenv("SERIAL_PORT", "/dev/ttyACM0")
BAUD_RATE = os.getenv("BAUD_RATE", 115200)
BACKEND_HOST = int(os.getenv("BACKEND_HOST", 127.0.0.1))
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

# Main loop
while True:
    try:
        line = ser.readline().decode('utf-8', errors='replace').strip()
        if line:
            print(f"Raw line: {line}")  # Optional: comment out if too noisy
            try:
                data = json.loads(line)
                print("Sending:", data)
                requests.post(f'http://{BACKEND_HOST}:{BACKEND_PORT}/log-entry', json=data)
            except json.JSONDecodeError as e:
                print("Invalid JSON received, skipping line.")
            except Exception as e:
                print("Error sending data:", e)
    except Exception as e:
        print("Error reading from serial:", e)
        time.sleep(1)
