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

log_info "Installing TTS and audio dependencies..."

# Install required system packages
log_info "Checking and installing system packages..."
PACKAGES=(
    "libttspico-utils"  # pico2wave
    "espeak-ng"         # espeak-ng
    "sox"               # audio processing
    "alsa-utils"        # aplay and ALSA tools
)

for pkg in "${PACKAGES[@]}"; do
    if ! dpkg -l | grep -q "^ii  $pkg"; then
        log_info "Installing $pkg..."
        sudo apt-get install -y "$pkg" || log_warn "Failed to install $pkg (optional)"
    else
        log_success "$pkg already installed"
    fi
done

# Add current user to audio group if not already
log_info "Adding $USER to audio group..."
if ! groups $USER | grep -q "\baudio\b"; then
    sudo usermod -a -G audio $USER
    log_success "Added $USER to audio group (you may need to log out and back in)"
else
    log_success "$USER is already in audio group"
fi

# Add klipper user to audio group if it exists
if id "klipper" &>/dev/null; then
    log_info "Adding klipper user to audio group..."
    if ! groups klipper | grep -q "\baudio\b"; then
        sudo usermod -a -G audio klipper
        log_success "Added klipper to audio group"
    else
        log_success "klipper is already in audio group"
    fi
fi

# Make speak.py executable
log_info "Making speak.py executable..."
chmod +x "$SCRIPT_DIR/speak.py"

# Test audio output
log_info "Testing audio output..."
if command -v aplay &>/dev/null; then
    log_info "Available audio devices:"
    aplay -L | head -20
    echo ""
    log_info "Testing with a simple beep..."
    if speaker-test -t sine -f 1000 -l 1 -s 1 >/dev/null 2>&1; then
        log_success "Audio test successful!"
    else
        log_warn "Audio test failed. Please check your audio configuration."
    fi
fi

# Test the speak script
log_info "Testing speak.py script..."
if "$SCRIPT_DIR/speak.py" "Setup complete" 2>/dev/null; then
    log_success "speak.py test successful!"
else
    log_warn "speak.py test failed. Check audio device configuration."
fi

echo ""
log_success "Setup complete!"
echo ""
log_info "Usage:"
echo "  1. Test from command line:"
echo "     $SCRIPT_DIR/speak.py \"Hello World\""
echo ""
echo "  2. Add to Klipper printer.cfg or shell_command.cfg:"
echo ""
echo "     [gcode_shell_command SPEAK_TEXT]"
echo "     command = python3 $SCRIPT_DIR/speak.py"
echo "     timeout = 5.0"
echo "     verbose: True"
echo ""
echo "     [gcode_macro SPEAK]"
echo "     gcode:"
echo "       RUN_SHELL_COMMAND CMD=SPEAK_TEXT PARAMS=\"{params.MSG|default('Hello World')}\""
echo ""
echo "  3. Test from Klipper console:"
echo "     SPEAK MSG=\"Test message\""
echo ""
log_info "Optional: Set custom audio device with environment variable:"
echo "     DEVICE=plughw:2,0 $SCRIPT_DIR/speak.py \"Test\""
echo ""

