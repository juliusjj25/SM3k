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
LOG_DIR = os.getenv("LOG_DIR", "smoker_logs")

app = Flask(__name__)
socketio = SocketIO(app)
os.makedirs(LOG_DIR, exist_ok=True)
active_log_file = None

<<<<<<< HEAD
<<<<<<< HEAD
=======
# Web page
>>>>>>> parent of 82097ca (Update to persistent data)
=======
# Web page
>>>>>>> parent of 82097ca (Update to persistent data)
@app.route('/')
def index():
    return render_template('index.html')

<<<<<<< HEAD
<<<<<<< HEAD
# ---------- Logs ----------
@app.route('/logs', methods=['GET'])
def list_logs():
    try:
        files = [f for f in os.listdir(LOG_DIR) if f.lower().endswith('.csv')]
        return jsonify(sorted(files))
    except Exception as e:
        return jsonify({'error': str(e)}), 500
=======
=======
>>>>>>> parent of 82097ca (Update to persistent data)
# List available logs
@app.route('/logs', methods=['GET'])
def list_logs():
    files = os.listdir(LOG_DIR)
    return jsonify(sorted(files))
>>>>>>> parent of 82097ca (Update to persistent data)

# Download a log
@app.route('/logs/<filename>', methods=['GET'])
<<<<<<< HEAD
<<<<<<< HEAD
def download_log(filename: str):
=======
def download_log(filename):
>>>>>>> parent of 82097ca (Update to persistent data)
=======
def download_log(filename):
>>>>>>> parent of 82097ca (Update to persistent data)
    return send_from_directory(LOG_DIR, filename, as_attachment=True)

# Delete a log
@app.route('/logs/<filename>', methods=['DELETE'])
<<<<<<< HEAD
<<<<<<< HEAD
def delete_log(filename: str):
=======
def delete_log(filename):
>>>>>>> parent of 82097ca (Update to persistent data)
=======
def delete_log(filename):
>>>>>>> parent of 82097ca (Update to persistent data)
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
    # Tell UIs to reset their chart
    socketio.emit('session-started', {'filename': name})
    return jsonify({'filename': name})

# Append a log entry (placeholder for ESP32 input)
@app.route('/log-entry', methods=['POST'])
def log_entry():
    global active_log_file
    if not active_log_file:
        return jsonify({'error': 'No active log file'}), 400

<<<<<<< HEAD
<<<<<<< HEAD
    data = request.get_json() or {}
=======
    data = request.get_json()
>>>>>>> parent of 82097ca (Update to persistent data)
=======
    data = request.get_json()
>>>>>>> parent of 82097ca (Update to persistent data)
    row = [
        datetime.datetime.now().isoformat(),
        data.get("chamber"),
        data.get("meat1"),
        data.get("meat2"),
        data.get("meat3"),
        data.get("meat4")
    ]
    with open(os.path.join(LOG_DIR, active_log_file), 'a', newline='') as f:
<<<<<<< HEAD
        csv.writer(f).writerow(row)
=======
        writer = csv.writer(f)
        writer.writerow(row)
<<<<<<< HEAD
>>>>>>> parent of 82097ca (Update to persistent data)
=======
>>>>>>> parent of 82097ca (Update to persistent data)

    socketio.emit('new-entry', row)
    return '', 204

@app.route('/stop-log', methods=['POST'])
def stop_log():
    global active_log_file
    active_log_file = None
    socketio.emit('session-stopped', {})
    return jsonify({'status': 'Logging stopped'})

# Real-time updates via WebSocket
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('status', {'msg': 'Connected to Smoker Backend'})
    
@app.route('/status', methods=['GET'])
def get_status():
<<<<<<< HEAD
<<<<<<< HEAD
    return jsonify({'active_log_file': active_log_file, 'log_dir': LOG_DIR})

# ---------- JSON views of logs ----------
@app.route('/logs/<filename>/json', methods=['GET'])
def get_log_json(filename: str):
    path = os.path.join(LOG_DIR, filename)
    if not os.path.exists(path):
        return jsonify({'error': 'File not found'}), 404
    entries = []
    with open(path, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            entry = {'Timestamp': row['Timestamp']}
            for key in ('ChamberTemp', 'Meat1', 'Meat2', 'Meat3', 'Meat4'):
                val = row.get(key)
                try:
                    entry[key] = float(val) if val not in (None, '', 'None') else None
                except ValueError:
                    entry[key] = None
            entries.append(entry)
    return jsonify(entries)

@app.route('/active-log/json', methods=['GET'])
def get_active_log_json():
    if not active_log_file:
        return jsonify([])
    return get_log_json(active_log_file)

# ---------- System stats ----------
=======
    return jsonify({'active_log_file': active_log_file})

>>>>>>> parent of 82097ca (Update to persistent data)
=======
    return jsonify({'active_log_file': active_log_file})

>>>>>>> parent of 82097ca (Update to persistent data)
def get_cpu_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            return round(int(f.read()) / 1000.0, 1)
    except:
        return None

@app.route('/system-stats')
def system_stats():
    cpu = psutil.cpu_percent(interval=0.5)
<<<<<<< HEAD
    mem = psutil.virtual_m_
=======
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
    print("Starting Flask app...")
<<<<<<< HEAD
    socketio.run(app, host='0.0.0.0', port=BACKEND_PORT)
>>>>>>> parent of 82097ca (Update to persistent data)
=======
    socketio.run(app, host='0.0.0.0', port=BACKEND_PORT)
>>>>>>> parent of 82097ca (Update to persistent data)
