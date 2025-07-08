import os
import time
import logging
import signal
import sys
import lgpio
import subprocess
import socket
import json
from logging.handlers import TimedRotatingFileHandler

print("PYTHON USED:", sys.executable)

# === CONFIGURABLE PATHS ===
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(SCRIPT_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "gpio_service.log")
POLL_INTERVAL = 0.1  # seconds

GPIO_PIN = 17  # BCM numbering for GPIO17

# === SETUP LOGGING ===
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("GPIOSwitchService")
logger.setLevel(logging.INFO)

handler = TimedRotatingFileHandler(
    LOG_FILE, when="midnight", interval=1, backupCount=7, encoding="utf-8"
)
handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s"))
handler.suffix = "%Y-%m-%d"
logger.addHandler(handler)

KLIPPER_RPC_ID = 1  # Global variable to track JSON-RPC id

def get_next_klipper_id():
    global KLIPPER_RPC_ID
    KLIPPER_RPC_ID += 1
    return KLIPPER_RPC_ID

def post_klipper_cmd(method, params=None):
    """Send a JSON-RPC command to Klipper and return the response."""
    sock_path = "/home/lianxu/printer_data/comms/klippy.sock"
    msg = {
        "id": get_next_klipper_id(),
        "method": method
    }
    if params is not None:
        msg["params"] = params
    logger.info(f"Sending JSON-RPC {method} to Klipper...")
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            logger.info(f"Connecting to Klipper socket at {sock_path}...")
            client.connect(sock_path)
            logger.info("Connected to Klipper socket. Sending message...")
            client.sendall((json.dumps(msg) + chr(0x03)).encode())
            logger.info("Message sent. Waiting for response...")
            response = b""
            while True:
                chunk = client.recv(4096)
                if not chunk:
                    break
                response += chunk
                if b"\x03" in chunk:
                    break
            logger.info(f"JSON-RPC {method} sent to Klipper! Response: {response.decode('utf-8').strip()}")
            return response.decode('utf-8').strip()
    except Exception as e:
        logger.error(f"Failed to send {method} to Klipper: {e}")
        return None

def setup_gpio():
    h = lgpio.gpiochip_open(0)
    lgpio.gpio_claim_input(h, GPIO_PIN, lgpio.SET_PULL_UP)
    return h

def cleanup_gpio(h):
    lgpio.gpiochip_close(h)

def main():
    logger.info(f"Starting GPIO17 key switch monitor on pin {GPIO_PIN}.")
    h = setup_gpio()
    last_state = lgpio.gpio_read(h, GPIO_PIN)
    logger.info(f"Initial GPIO{GPIO_PIN} state: {'PRESSED' if last_state == 0 else 'RELEASED'}")

    try:
        while True:
            current_state = lgpio.gpio_read(h, GPIO_PIN)
            if current_state != last_state:
                if current_state == 0:
                    logger.info("Key switch PRESSED (GPIO17 LOW).")
                else:
                    logger.info("Key switch RELEASED (GPIO17 HIGH).")
                    post_klipper_cmd("emergency_stop")
                    time.sleep(3)
                    post_klipper_cmd("gcode/firmware_restart")
                last_state = current_state
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        logger.info("GPIO service stopped by user.")
    finally:
        cleanup_gpio(h)
        logger.info("GPIO cleaned up.")

if __name__ == "__main__":
    main()
