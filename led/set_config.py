#!/usr/bin/env python3
import sys
import configparser
import logging
import os
from pathlib import Path


# Get the directory where this script lives
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "led_config.ini")
LOG_DIR = os.path.join(SCRIPT_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "set_config.log")

os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
)

def update_config(pairs):
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)

    if "led" not in config:
        config["led"] = {}

    for pair in pairs:
        if '=' in pair:
            key, value = pair.split('=', 1)
            config["led"][key.strip()] = value.strip()
            logging.info(f"Set {key.strip()} = {value.strip()}")
        else:
            logging.warning(f"Ignored invalid argument: {pair}")

    with open(CONFIG_PATH, "w") as f:
        config.write(f)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: set_config.py key=value [key2=value2 ...]")
        logging.info(f"Usage sys.argv: {sys.argv}")
        sys.exit(1)

    logging.info(f"Received arguments: {sys.argv[1:]}")
    update_config(sys.argv[1:])
