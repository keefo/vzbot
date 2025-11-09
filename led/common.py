import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.expanduser("~/printer_data/config/led_config.ini")
LOG_DIR = os.path.join(SCRIPT_DIR, "logs")
SERVICE_POLL_INTERVAL = 1  # seconds
PYTHON_PATH = os.path.join(SCRIPT_DIR, "venv/bin/python3")
WLED_IP = "vzbot-wled.local"  # WLED controller hostname or IP
LED_COUNT = 21  # Number of LEDs in the strip
