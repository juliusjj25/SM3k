#!/bin/bash

# Load environment variables
set -a
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
if [ -f "$PROJECT_DIR/backend/.env" ]; then
  source "$PROJECT_DIR/backend/.env"
fi
set +a

cd "$PROJECT_DIR/backend"
source venv/bin/activate
python3 app.py --port "${BACKEND_PORT:-8080}"