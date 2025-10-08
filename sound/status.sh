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

echo "========================================="
echo "Sound/TTS System Status"
echo "========================================="
echo ""

# Check script permissions
log_info "Checking speak.py..."
if [ -x "$SCRIPT_DIR/speak.py" ]; then
    log_success "speak.py is executable"
else
    log_error "speak.py is not executable"
fi

# Check TTS engines
log_info "Checking TTS engines..."
if command -v pico2wave &>/dev/null; then
    log_success "pico2wave installed"
else
    log_warn "pico2wave not installed"
fi

if command -v espeak-ng &>/dev/null; then
    log_success "espeak-ng installed"
else
    log_warn "espeak-ng not installed"
fi

if command -v piper &>/dev/null; then
    log_success "piper installed"
else
    log_warn "piper not installed (optional)"
fi

# Check audio tools
log_info "Checking audio tools..."
if command -v aplay &>/dev/null; then
    log_success "aplay installed"
else
    log_error "aplay not installed"
fi

if command -v sox &>/dev/null; then
    log_success "sox installed"
else
    log_warn "sox not installed (optional)"
fi

# Check audio group membership
log_info "Checking audio group membership..."
if groups $USER | grep -q "\baudio\b"; then
    log_success "$USER is in audio group"
else
    log_error "$USER is NOT in audio group"
fi

if id "klipper" &>/dev/null; then
    if groups klipper | grep -q "\baudio\b"; then
        log_success "klipper user is in audio group"
    else
        log_error "klipper user is NOT in audio group"
    fi
fi

# List audio devices
echo ""
log_info "Available audio devices:"
if command -v aplay &>/dev/null; then
    aplay -L | grep -E "^(default|pulse|plughw)" | head -10
else
    log_error "aplay not available"
fi

# Test the script
echo ""
log_info "Testing speak.py script..."
if timeout 5 "$SCRIPT_DIR/speak.py" "Status check" 2>&1 >/dev/null; then
    log_success "speak.py executed successfully"
else
    log_warn "speak.py test failed or timed out"
fi

echo ""
echo "========================================="
echo "To test manually, run:"
echo "  $SCRIPT_DIR/speak.py \"Test message\""
echo "========================================="
