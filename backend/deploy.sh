#!/bin/bash

# Define project paths dynamically
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
SERVICE_DIR="$PROJECT_DIR/config/systemd"
NGINX_DIR="$PROJECT_DIR/config/nginx"
DUCKDNS_DIR="$PROJECT_DIR/config/duckdns"
CGI_DIR="$PROJECT_DIR/cgi-bin"

# Clone the repo if needed
if [ ! -d "$PROJECT_DIR/.git" ]; then
  git clone --depth 1 https://github.com/juliusjj25/SM3k.git "$PROJECT_DIR"
else
  git -C "$PROJECT_DIR" pull --ff-only
fi

# Ensure virtual environment exists
if [ ! -d "$BACKEND_DIR/venv" ]; then
  python3 -m venv "$BACKEND_DIR/venv"
fi

# Install Python dependencies
source "$BACKEND_DIR/venv/bin/activate"
pip install --upgrade pip
pip install -r "$BACKEND_DIR/requirements.txt"

# Ensure python-dotenv is installed
if ! pip show python-dotenv > /dev/null 2>&1; then
  pip install python-dotenv
fi
deactivate

# Fix .env format if needed (prepend export if missing)
ENV_FILE="$BACKEND_DIR/.env"
if [ -f "$ENV_FILE" ]; then
  grep -q '^export ' "$ENV_FILE" || sed -i 's/^/export /' "$ENV_FILE"
elif [ -f "$BACKEND_DIR/.env.example" ]; then
  cp "$BACKEND_DIR/.env.example" "$ENV_FILE"
  sed -i 's/^/export /' "$ENV_FILE"
fi

# Install systemd services
sudo install -m 644 "$SERVICE_DIR"/smoker-backend.service /etc/systemd/system/
sudo install -m 644 "$SERVICE_DIR"/serial-bridge.service /etc/systemd/system/

# Ensure system packages are installed
sudo apt update
sudo apt install -y nginx fcgiwrap certbot python3-certbot-nginx

# Install nginx config
sudo install -m 644 "$NGINX_DIR"/default /etc/nginx/sites-available/sm3k
sudo ln -sf /etc/nginx/sites-available/sm3k /etc/nginx/sites-enabled/sm3k

# Install duck.sh
sudo install -m 755 "$DUCKDNS_DIR/duck.sh" /usr/local/bin/duck.sh

# Install CGI scripts
sudo mkdir -p /usr/lib/cgi-bin
sudo install -m 755 "$CGI_DIR"/* /usr/lib/cgi-bin/

# Install post-merge git hook
HOOKS_SRC="$PROJECT_DIR/scripts/git-hooks/post-merge"
if [ -f "$HOOKS_SRC" ]; then
  cp "$HOOKS_SRC" "$PROJECT_DIR/.git/hooks/post-merge"
  chmod +x "$PROJECT_DIR/.git/hooks/post-merge"
fi

# Reload systemd and restart services
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl restart smoker-backend.service
sudo systemctl restart serial-bridge.service

echo "Deploy script complete."
