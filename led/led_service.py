import os
import time
import subprocess
import hashlib
import logging
import signal
import sys
from logging.handlers import TimedRotatingFileHandler

print("PYTHON USED:", sys.executable)

# === CONFIGURABLE PATHS ===
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_PATH = os.path.join(SCRIPT_DIR, "venv/bin/python3")
CONFIG_PATH = os.path.join(SCRIPT_DIR, "led_config.ini")
SCRIPT_PATH = os.path.join(SCRIPT_DIR, "set.py")
LOG_DIR = os.path.join(SCRIPT_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "led_service.log")
POLL_INTERVAL = 1  # seconds

# === SETUP LOGGING ===
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("LEDService")
logger.setLevel(logging.INFO)

handler = TimedRotatingFileHandler(
    LOG_FILE, when="midnight", interval=1, backupCount=7, encoding="utf-8"
)
handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s"))
handler.suffix = "%Y-%m-%d"
logger.addHandler(handler)

# === FUNCTION TO HASH CONFIG FILE CONTENTS ===
def get_file_hash(filepath):
    try:
        with open(filepath, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except FileNotFoundError:
        logger.warning(f"Config file not found: {filepath}")
        return None
    except Exception as e:
        logger.error(f"Error reading config file: {e}")
        return None

# === HANDLE RESTART OF SET.PY ===
def restart_led_script(current_proc):
    """Terminate existing script and start a new one."""
    if current_proc:
        if current_proc.poll() is None:
            logger.info("Terminating previous LED script...")
            current_proc.terminate()
            try:
                current_proc.wait(timeout=3)
                logger.info("Previous script terminated cleanly.")
            except subprocess.TimeoutExpired:
                logger.warning("Script did not exit in time. Killing forcefully...")
                current_proc.kill()
                current_proc.wait()
        else:
            logger.info(f"Previous script had exited with code {current_proc.returncode}")

    try:
        new_proc = subprocess.Popen([PYTHON_PATH, SCRIPT_PATH])
        logger.info(f"Started new LED script: PID={new_proc.pid}")
        return new_proc
    except Exception as e:
        logger.exception("Failed to start LED script")
        return None

# === MAIN LOOP ===
def main():
    logger.info(f"Starting LED service. Monitoring: {CONFIG_PATH}")
    last_hash = get_file_hash(CONFIG_PATH)
    process = None

    while True:
        time.sleep(POLL_INTERVAL)
        current_hash = get_file_hash(CONFIG_PATH)

        # Check for config changes
        if current_hash and current_hash != last_hash:
            logger.info("Config file changed. Restarting LED update script...")
            process = restart_led_script(process)
            last_hash = current_hash

        # Clean up defunct process if it quit
        if process and process.poll() is not None:
            logger.info(f"LED script exited with code {process.returncode}")
            process = None

if __name__ == "__main__":
    try:
        logger.info("LED service started.")
        logger.info(f"PYTHON_PATH: {PYTHON_PATH}")
        main()
    except KeyboardInterrupt:
        logger.info("LED service stopped by user.")
