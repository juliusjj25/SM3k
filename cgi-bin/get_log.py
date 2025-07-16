#!/usr/bin/env python3
import os
import cgi
from dotenv import load_dotenv

LOG_DIR = os.getenv("LOG_DIR", "/home/juliusjj25/SM3k/smoke_sessions")

form = cgi.FieldStorage()
filename = form.getvalue("file")

if filename and ".." not in filename:
    filepath = os.path.join(LOG_DIR, filename)
    if os.path.isfile(filepath):
        print(f"Content-Type: text/csv")
        print(f"Content-Disposition: attachment; filename=\"{filename}\"\n")
        with open(filepath, 'r') as f:
            print(f.read())
    else:
        print("Content-Type: text/plain\n")
        print("File not found.")
else:
    print("Content-Type: text/plain\n")
    print("Invalid file name.")
