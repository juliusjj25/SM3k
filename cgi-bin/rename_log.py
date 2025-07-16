#!/usr/bin/env python3
import os
import cgi
from dotenv import load_dotenv

LOG_DIR = os.getenv("LOG_DIR", "/home/juliusjj25/SM3k/smoke_sessions")
form = cgi.FieldStorage()

old_name = form.getvalue("old_name")
new_name = form.getvalue("new_name")

print("Content-Type: text/html\n")

if old_name and new_name and ".." not in old_name and ".." not in new_name:
    old_path = os.path.join(LOG_DIR, old_name)
    new_path = os.path.join(LOG_DIR, new_name)
    try:
        os.rename(old_path, new_path)
        print(f"<p>Renamed {old_name} to {new_name}</p>")
    except Exception as e:
        print(f"<p>Error renaming: {e}</p>")
else:
    print("<p>Invalid input.</p>")

print('<p><a href="/cgi-bin/list_logs.py">Back to logs</a></p>')
