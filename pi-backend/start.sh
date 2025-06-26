#!/bin/bash
cd /home/juliusjj25/smoker-backend
source venv/bin/activate
exec gunicorn --worker-class eventlet -w 1 app:app --bind 0.0.0.0:5000
