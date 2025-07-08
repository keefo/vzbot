#!/bin/bash

# Color definitions
GREEN='\033[0;32m'
BLUE='\033[1;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Helper for status messages
log_info()    { echo -e "${BLUE}[*] $1${NC}"; }
log_success() { echo -e "${GREEN}[✓] $1${NC}"; }
log_warn()    { echo -e "${YELLOW}[!] $1${NC}"; }
log_error()   { echo -e "${RED}[✗] $1${NC}"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/venv"
PYTHON_PATH="$VENV_PATH/bin/python3"
SVS_SCRIPT="$SCRIPT_DIR/killswitch_service.py"
SERVICE_FILE="/etc/systemd/system/killswitch_service.service"

log_info "Creating Python virtual environment..."
python3 -m venv "$VENV_PATH"
source "$VENV_PATH/bin/activate"

log_info "Installing dependencies..."
pip install --upgrade pip
pip install -r "$SCRIPT_DIR/requirements.txt" || log_error "Failed to install dependencies"

log_info "Creating systemd service file at $SERVICE_FILE..."

sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=KillSwitch Button service
After=multi-user.target

[Service]
ExecStart=$PYTHON_PATH $SVS_SCRIPT
WorkingDirectory=$SCRIPT_DIR
StandardOutput=journal
StandardError=journal
Restart=always
User=$USER

[Install]
WantedBy=multi-user.target
EOF

log_info "Reloading systemd and enabling service..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable killswitch_service.service
sudo systemctl restart killswitch_service.service

log_success "Done! KillSwitch Button service is installed and running."
