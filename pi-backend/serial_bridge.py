import time
import serial
import requests
import json
import os

SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 115200

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
                requests.post('http://127.0.0.1:5000/log-entry', json=data)
            except json.JSONDecodeError as e:
                print("Invalid JSON received, skipping line.")
            except Exception as e:
                print("Error sending data:", e)
    except Exception as e:
        print("Error reading from serial:", e)
        time.sleep(1)
