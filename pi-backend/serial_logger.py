import serial
import time
import sys

SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 115200

def log_serial(filename):
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser, open(filename, 'a') as f:
            print(f"Logging to {filename}")
            while True:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    print(line)
                    f.write(line + '\n')
                    f.flush()
    except KeyboardInterrupt:
        print("Logging stopped.")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 serial_logger.py <filename>")
        sys.exit(1)
    log_serial(sys.argv[1])
