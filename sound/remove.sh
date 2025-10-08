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

log_info "This will remove TTS sound configuration from your system."
log_warn "Note: This will NOT remove system packages (pico2wave, espeak-ng, sox, etc.)"
log_warn "      You can remove them manually with: sudo apt-get remove <package>"
echo ""

read -p "Continue? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "Cancelled."
    exit 0
fi

# Instructions for removing from Klipper
log_info "To complete removal, you should also:"
echo ""
echo "1. Remove the following from your Klipper config files:"
echo "   - [gcode_shell_command SPEAK_TEXT]"
echo "   - [gcode_macro SPEAK]"
echo ""
echo "2. Restart Klipper after removing the config"
echo ""

log_success "Cleanup complete!"
