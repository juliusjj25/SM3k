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

@app.route('/')
def index():
    return render_template('index.html')

# ---------- Logs ----------
@app.route('/logs', methods=['GET'])
def list_logs():
    try:
        files = [f for f in os.listdir(LOG_DIR) if f.lower().endswith('.csv')]
        return jsonify(sorted(files))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/logs/<filename>', methods=['GET'])
def download_log(filename: str):
    return send_from_directory(LOG_DIR, filename, as_attachment=True)

@app.route('/logs/<filename>', methods=['DELETE'])
def delete_log(filename: str):
    try:
        os.remove(os.path.join(LOG_DIR, filename))
        return '', 204
    except Exception:
        return 'Error deleting file', 500

@app.route('/start-log', methods=['POST'])
def start_log():
    global active_log_file
    data = request.get_json() or {}
    name = data.get('filename') or datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S.csv")
    path = os.path.join(LOG_DIR, name)
    active_log_file = name
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "ChamberTemp", "Meat1", "Meat2", "Meat3", "Meat4"])
    # Tell UIs to reset their chart
    socketio.emit('session-started', {'filename': name})
    return jsonify({'filename': name})

@app.route('/log-entry', methods=['POST'])
def log_entry():
    global active_log_file
    if not active_log_file:
        return jsonify({'error': 'No active log file'}), 400

    data = request.get_json() or {}
    row = [
        datetime.datetime.now().isoformat(),
        data.get("chamber"),
        data.get("meat1"),
        data.get("meat2"),
        data.get("meat3"),
        data.get("meat4")
    ]
    with open(os.path.join(LOG_DIR, active_log_file), 'a', newline='') as f:
        csv.writer(f).writerow(row)

    socketio.emit('new-entry', row)
    return '', 204

@app.route('/stop-log', methods=['POST'])
def stop_log():
    global active_log_file
    active_log_file = None
    socketio.emit('session-stopped', {})
    return jsonify({'status': 'Logging stopped'})

@app.route('/status', methods=['GET'])
def get_status():
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
def get_cpu_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            return round(int(f.read()) / 1000.0, 1)
    except Exception:
        return None

@app.route('/system-stats')
def system_stats():
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_m_
