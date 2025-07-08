#!/bin/bash

# Load environment variables
set -a
source /home/juliusjj25/SM3K/backend/.env
set +a

cd "$PROJECT_ROOT/backend"
source "$VENV_PATH/bin/activate"
exec gunicorn --worker-class eventlet -w 1 app:app --bind 0.0.0.0:$BACKEND_PORT
