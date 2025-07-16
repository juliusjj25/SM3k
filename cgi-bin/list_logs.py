#!/usr/bin/env python3
import os
from dotenv import load_dotenv

LOG_DIR = os.getenv("LOG_DIR", "/home/juliusjj25/SM3k/smoke_sessions")
print("Content-Type: text/html\n")
print("<html><body><h2>Smoker Logs</h2><ul>")

for filename in sorted(os.listdir(LOG_DIR)):
    full_path = os.path.join(LOG_DIR, filename)
    if os.path.isfile(full_path):
        print(f'''
            <li>
                <a href="/cgi-bin/get_log.py?file={filename}">{filename}</a>
                <form method="POST" action="/cgi-bin/delete_log.py" style="display:inline;">
                    <input type="hidden" name="file" value="{filename}">
                    <input type="submit" value="Delete">
                </form>
                <form method="POST" action="/cgi-bin/rename_log.py" style="display:inline;">
                    <input type="hidden" name="old_name" value="{filename}">
                    <input type="text" name="new_name" placeholder="New name" required>
                    <input type="submit" value="Rename">
                </form>
            </li>
        ''')

print("</ul></body></html>")
