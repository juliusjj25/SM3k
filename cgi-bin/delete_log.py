#!/usr/bin/env python3
import os
import cgi
from dotenv import load_dotenv

LOG_DIR = os.getenv("LOG_DIR", "/home/juliusjj25/SM3k/smoke_sessions")
form = cgi.FieldStorage()
filename = form.getvalue("file")

print("Content-Type: text/html\n")

if filename and ".." not in filename:
    path = os.path.join(LOG_DIR, filename)
    try:
        os.remove(path)
        print(f"<p>Deleted: {filename}</p>")
    except Exception as e:
        print(f"<p>Error deleting: {e}</p>")
else:
    print("<p>Invalid file name.</p>")

print('<p><a href="/cgi-bin/list_logs.py">Back to logs</a></p>')
