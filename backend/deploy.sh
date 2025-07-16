#!/bin/bash

# Define variables
PROJECT_DIR="/home/juliusjj25/SM3k"
BACKEND_DIR="$PROJECT_DIR/backend"
VENV_DIR="$BACKEND_DIR/venv"

# Clone the repo if it doesn't exist
if [ ! -d "$PROJECT_DIR/.git" ]; then
    git clone git@github.com:juliusjj25/SM3k.git "$PROJECT_DIR"
else
    cd "$PROJECT_DIR"
    git remote set-url origin git@github.com:juliusjj25/SM3k.git
    git pull
fi


# Set correct permissions
chown -R juliusjj25:juliusjj25 "$PROJECT_DIR"
chmod -R u+rwX,g+rX,o-rwx "$PROJECT_DIR"

# Set up the virtual environment if not already
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi

# Activate venv and install requirements
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r "$BACKEND_DIR/requirements.txt"

# Copy systemd service files
sudo cp "$PROJECT_DIR/config/systemd/smoker-backend.service" /etc/systemd/system/
sudo cp "$PROJECT_DIR/config/systemd/serial-bridge.service" /etc/systemd/system/
sudo chmod 644 /etc/systemd/system/smoker-backend.service
sudo chmod 644 /etc/systemd/system/serial-bridge.service

# Reload systemd and enable services
sudo systemctl daemon-reexec
sudo systemctl enable smoker-backend.service
sudo systemctl enable serial-bridge.service

# Restart services
sudo systemctl restart smoker-backend.service
sudo systemctl restart serial-bridge.service

# Copy nginx config and set permissions
sudo cp "$PROJECT_DIR/config/nginx/default" /etc/nginx/sites-available/sm3k
sudo ln -sf /etc/nginx/sites-available/sm3k /etc/nginx/sites-enabled/sm3k
sudo chmod 644 /etc/nginx/sites-available/sm3k
sudo systemctl restart nginx

# Copy DuckDNS script and set executable
sudo cp "$PROJECT_DIR/config/duckdns/duck.sh" /usr/local/bin/duck.sh
sudo chmod +x /usr/local/bin/duck.sh

# Add cron job for DuckDNS if not already
(crontab -l 2>/dev/null | grep -q 'duck.sh') || (crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/duck.sh >/dev/null 2>&1") | crontab -

# Install CGI Scripts
sudo mkdir -p /usr/lib/cgi-bin
sudo cp -f "$PROJECT_DIR/cgi-bin/"*.py /usr/lib/cgi-bin/
sudo chown root:root /usr/lib/cgi-bin/*.py
sudo chmod 755 /usr/lib/cgi-bin/*.py

# Copy .env file to backend directory
cp "$PROJECT_DIR/backend/.env" "$BACKEND_DIR/.env"

# Fix permissions again to be sure
chown -R juliusjj25:juliusjj25 "$PROJECT_DIR"
chmod -R u+rwX,g+rX,o-rwx "$PROJECT_DIR"

# Done
echo "Deployment complete. Check with: journalctl -u smoker-backend.service -f"
