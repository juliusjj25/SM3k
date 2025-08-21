from flask import Flask, render_template, request, send_from_directory, jsonify
from flask_socketio import SocketIO, emit
import datetime
import csv
from dotenv import load_dotenv
import os
import psutil
import shutil

load_dotenv()

BACKEND_PORT = int(os.getenv("BACKEND_PORT", 5000))

app = Flask(__name__)
socketio = SocketIO(app)
LOG_DIR = "smoker_logs"
os.makedirs(LOG_DIR, exist_ok=True)
active_log_file = None

# Web page
@app.route('/')
def index():
    return render_template('index.html')

# List available logs
@app.route('/logs', methods=['GET'])
def list_logs():
    files = os.listdir(LOG_DIR)
    return jsonify(sorted(files))

# Download a log
@app.route('/logs/<filename>', methods=['GET'])
def download_log(filename):
    return send_from_directory(LOG_DIR, filename, as_attachment=True)

# Delete a log
@app.route('/logs/<filename>', methods=['DELETE'])
def delete_log(filename):
    try:
        os.remove(os.path.join(LOG_DIR, filename))
        return '', 204
    except:
        return 'Error deleting file', 500

# Start a log
@app.route('/start-log', methods=['POST'])
def start_log():
    global active_log_file
    data = request.get_json()
    name = data.get('filename') or datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S.csv")
    path = os.path.join(LOG_DIR, name)
    active_log_file = name
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "ChamberTemp", "Meat1", "Meat2", "Meat3", "Meat4"])
    return jsonify({'filename': name})

# Append a log entry (placeholder for ESP32 input)
@app.route('/log-entry', methods=['POST'])
def log_entry():
    global active_log_file
    if not active_log_file:
        return jsonify({'error': 'No active log file'}), 400

    data = request.get_json()
    row = [
        datetime.datetime.now().isoformat(),
        data.get("chamber"),
        data.get("meat1"),
        data.get("meat2"),
        data.get("meat3"),
        data.get("meat4")
    ]
    with open(os.path.join(LOG_DIR, active_log_file), 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(row)

    socketio.emit('new-entry', row)
    return '', 204

@app.route('/stop-log', methods=['POST'])
def stop_log():
    global active_log_file
    active_log_file = None
    return jsonify({'status': 'Logging stopped'})

# Real-time updates via WebSocket
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('status', {'msg': 'Connected to Smoker Backend'})
    
@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({'active_log_file': active_log_file})

@app.route('/system-stats')
def system_stats():
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory()
    disk = shutil.disk_usage("/")
    temp = get_cpu_temp()

    return {
        'cpu': cpu,
        'mem': mem.percent,
        'mem_used': mem.used / (1024 * 1024),
        'mem_total': mem.total / (1024 * 1024),
        'disk_used': disk.used,
        'disk_total': disk.total,
        'temp': temp
    }

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=BACKEND_PORT)

def get_cpu_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            return round(int(f.read()) / 1000.0, 1)
    except:
        return None

def get_cpu_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            return round(int(f.read()) / 1000, 1)
    except:
        return None