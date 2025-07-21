import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.expanduser("~/printer_data/config/led_config.ini")
LOG_DIR = os.path.join(SCRIPT_DIR, "logs")
SERVICE_POLL_INTERVAL = 1  # seconds
PYTHON_PATH = os.path.join(SCRIPT_DIR, "venv/bin/python3")
