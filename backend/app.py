from flask import Flask, render_template, request, send_from_directory, jsonify
from flask_socketio import SocketIO, emit
import datetime
import csv
from dotenv import load_dotenv
import os
import psutil
import shutil

"""
This Flask application forms the backend of the SmokerMaster3000 project.  It
provides HTTP endpoints for managing log files, streaming system statistics,
and broadcasting real‑time temperature updates to all connected clients via
WebSockets.  To support persisting data across page reloads and multiple
devices, new routes have been added to expose log data as JSON and to send
historical entries to newly connected clients.  See the corresponding
index.html for client‑side logic consuming these endpoints.
"""

load_dotenv()

BACKEND_PORT = int(os.getenv("BACKEND_PORT", 5000))

app = Flask(__name__)
socketio = SocketIO(app)
LOG_DIR = "smoker_logs"
os.makedirs(LOG_DIR, exist_ok=True)
active_log_file = None

# ---------------------------------------------------------------------------
#  Routes for HTML and static assets
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    """Render the main dashboard page."""
    return render_template('index.html')

# ---------------------------------------------------------------------------
#  Log management endpoints
# ---------------------------------------------------------------------------

@app.route('/logs', methods=['GET'])
def list_logs():
    """Return the list of available log filenames sorted alphabetically."""
    files = os.listdir(LOG_DIR)
    return jsonify(sorted(files))

@app.route('/logs/<filename>', methods=['GET'])
def download_log(filename: str):
    """Stream a log file to the client for download."""
    return send_from_directory(LOG_DIR, filename, as_attachment=True)

@app.route('/logs/<filename>', methods=['DELETE'])
def delete_log(filename: str):
    """Delete the specified log file from the filesystem."""
    try:
        os.remove(os.path.join(LOG_DIR, filename))
        return '', 204
    except Exception:
        return 'Error deleting file', 500

@app.route('/start-log', methods=['POST'])
def start_log():
    """
    Begin logging to a new CSV file.  A filename may be provided in the
    request body; otherwise a timestamp‑based name is generated.  The header
    row is written immediately.  Returns the name of the started file.
    """
    global active_log_file
    data = request.get_json() or {}
    name = data.get('filename') or datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S.csv")
    path = os.path.join(LOG_DIR, name)
    active_log_file = name
    # Create file and write header
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "ChamberTemp", "Meat1", "Meat2", "Meat3", "Meat4"])
    return jsonify({'filename': name})

@app.route('/log-entry', methods=['POST'])
def log_entry():
    """
    Append a new temperature reading to the active log file.  The request body
    should contain keys 'chamber', 'meat1', 'meat2', 'meat3' and 'meat4'.  Each
    entry is timestamped on the server.  The appended row is broadcast via
    WebSockets so connected dashboards can update in real time.
    """
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
        writer = csv.writer(f)
        writer.writerow(row)
    # Notify clients of the new entry
    socketio.emit('new-entry', row)
    return '', 204

@app.route('/stop-log', methods=['POST'])
def stop_log():
    """Stop logging by clearing the active_log_file reference."""
    global active_log_file
    active_log_file = None
    return jsonify({'status': 'Logging stopped'})

@app.route('/status', methods=['GET'])
def get_status():
    """Expose the currently active log file name or null if none."""
    return jsonify({'active_log_file': active_log_file})

# ---------------------------------------------------------------------------
#  New endpoints for persisted data
# ---------------------------------------------------------------------------

@app.route('/logs/<filename>/json', methods=['GET'])
def get_log_json(filename: str):
    """
    Read the specified CSV log file and return its contents as a JSON array.
    Numeric values are coerced to floats when possible.  Returns 404 if the
    file does not exist.
    """
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
    """
    Convenience route to fetch the current active log's contents in JSON
    format.  If no log is active an empty list is returned.
    """
    if not active_log_file:
        return jsonify([])
    return get_log_json(active_log_file)

# ---------------------------------------------------------------------------
#  System status and helper functions
# ---------------------------------------------------------------------------

def get_cpu_temp():
    """Attempt to read the CPU temperature on systems where it's available."""
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            return round(int(f.read()) / 1000.0, 1)
    except Exception:
        return None

@app.route('/system-stats')
def system_stats():
    """
    Return basic system metrics such as CPU usage, memory usage, disk usage
    and temperature.  Used by the dashboard to show Raspberry Pi status.
    """
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

# ---------------------------------------------------------------------------
#  WebSocket handlers
# ---------------------------------------------------------------------------

@socketio.on('connect')
def handle_connect():
    """
    When a client connects via WebSockets, send them the existing log entries
    (if a log is active) before streaming new entries.  Also send a simple
    status message confirming connection.
    """
    if active_log_file:
        path = os.path.join(LOG_DIR, active_log_file)
        if os.path.exists(path):
            entries = []
            with open(path, 'r', newline='') as f:
                reader = csv.reader(f)
                header = next(reader, None)
                for row in reader:
                    entries.append(row)
            emit('init-log', entries)
    emit('status', {'msg': 'Connected to Smoker Backend'})

if __name__ == '__main__':
    print("Starting Flask app...")
    socketio.run(app, host='0.0.0.0', port=BACKEND_PORT)
