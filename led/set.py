import os
import configparser
import logging
import board
import colorsys
import time
import adafruit_pixelbuf
from adafruit_raspberry_pi5_neopixel_write import neopixel_write

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "led_config.ini")
LOG_DIR = os.path.join(SCRIPT_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "set.log")
PIN = board.D10
LED_COUNT = 21

os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
)

class SK6812_RGBW(adafruit_pixelbuf.PixelBuf):
    def __init__(self, pin, size, **kwargs):
        self._pin = pin
        super().__init__(size=size, byteorder="WRGB", **kwargs)

    def _transmit(self, buf):
        neopixel_write(self._pin, buf)

    def set_back(self, color):
        for i in range(0, 5):
            self[i] = color

    def set_back(self, color):
        for i in range(0, 5):
            self[i] = color

    def set_right(self, color):
        for i in range(5, 10):
            self[i] = color

    def set_front(self, color):
        for i in range(10, 15):
            self[i] = color

    def set_left(self, color):
        for i in range(15, 20):
            self[i] = color

    def set_rainbow(self):
        logging.info(f"set_rainbow len(self)")
        for i in range(len(self)):
            hue = i / len(self)  # even spread from 0.0 to <1.0
            r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(hue, 1.0, 1.0)]
            logging.info(f"set_rainbow {i} ({r}, {g}, {b})")
            self[i] = (r, g, b, 0)  # SK6812 RGBW: (R, G, B, W)
    
    def animate_rainbow(self, delay=0.5):
        num_leds = len(self)
        logging.info(f"animate_rainbow start: num_leds={num_leds}")
        frame = 0

        while True:
            base_hue = (frame / float(num_leds)) % 1.0
            for i in range(num_leds):
                hue = (base_hue + i / num_leds) % 1.0
                r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(hue, 1.0, 1.0)]
                self[i] = (r, g, b, 0)
            self.show()
            time.sleep(delay)
            frame += 1

    def animate_xmas(self, delay=0.5):
        colors = [(255, 0, 0, 0), (0, 255, 0, 0), (255, 255, 255, 0)]  # red, green, white
        pattern = [colors[i % len(colors)] for i in range(len(self))]
        logging.info("Starting animate_xmas")
        while True:
            for i in range(len(self)):
                self[i] = pattern[i]
            self.show()
            pattern = pattern[-1:] + pattern[:-1]  # rotate right
            time.sleep(delay)



def main():
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_FILE):
        logging.error(f"Missing config file: {CONFIG_FILE}")
        return

    config.read(CONFIG_FILE)

    if "led" not in config:
        logging.error("Missing [led] section in config file.")
        return
    
    white = 0
    try:
        section = config["led"]
        pattern = str(section.get("pattern", ""))
        white = int(section.get("white", "0x00"), 00)
        brightness = float(section.get("brightness", 0.3))
    except Exception as e:
        logging.exception("Failed to parse LED config")
        return
 
    r = 0
    g = 0
    b = 0
    w = white

    logging.info(f"Setting LEDs to pattern={pattern}")
    # help convert pattern to r, g, b, w
    # if pattern start with 0x, it is a hex color
    # if pattern is red ,blue, green, yellow, purple, orange, pink, brown, gray, black, white, cyan, magenta, lime, maroon, navy, olive, purple, teal, or violet, it is a color
    if pattern == "off":        
        r = 0
        g = 0
        b = 0
        w = 0
        brightness = 0
    elif pattern.startswith("0x"):
        r = int(pattern[2:4], 16)
        g = int(pattern[4:6], 16)
        b = int(pattern[6:8], 16)
    # give me correct color based on keyword
    elif pattern == "red":
        r = 255
    elif pattern == "blue": 
        b = 255
    elif pattern == "green":
        g = 255
    elif pattern == "yellow":
        r = 255
        g = 255 
    elif pattern == "purple":
        r = 128
        b = 128
    elif pattern == "orange":
        r = 255
        g = 165
    elif pattern == "pink":
        r = 255
        g = 192
        b = 203
    elif pattern == "brown":
        r = 165
        g = 42
        b = 42
    elif pattern == "black":
        r = 0   
        g = 0
        b = 0
        w = 0
    elif pattern == "white":
        r = 255
        g = 255
        b = 255
        w = 255
    elif pattern == "sunset":
        r = 252
        g = 94
        b = 3
        w = 0
    elif pattern == "demo":
        try:
            pixels = SK6812_RGBW(PIN, LED_COUNT, brightness=brightness, auto_write=True)
            # Set color segments
            pixels.set_back((255, 255, 255, 255))
            pixels.set_right((255, 0, 0, 20))
            pixels.set_front((255, 255, 255, 255))
            pixels.set_left((0, 0, 255, 20))
            pixels.show()
            logging.info("LEDs updated successfully.")
        except Exception as e:
            logging.exception("Failed to apply LED config")
        return
    elif pattern == "rainbow":
        try:
            pixels = SK6812_RGBW(PIN, LED_COUNT, brightness=brightness, auto_write=True)
            # Set color segments
            pixels.animate_rainbow()
            pixels.show()
            logging.info("LEDs updated successfully.")
        except Exception as e:
            logging.exception("Failed to apply LED config")
        return
    elif pattern == "xmas":
        try:
            pixels = SK6812_RGBW(PIN, LED_COUNT, brightness=brightness, auto_write=True)
            # Set color segments
            pixels.animate_xmas()
            pixels.show()
            logging.info("LEDs updated successfully.")
        except Exception as e:
            logging.exception("Failed to apply LED config")
        return

    logging.info(f"Setting LEDs to pattern={pattern} white={white} brightness {brightness}")

    try:
        pixels = SK6812_RGBW(PIN, LED_COUNT, brightness=brightness, auto_write=True)
        pixels.fill((r, g, b, w))
        logging.info("LEDs updated successfully.")
    except Exception as e:
        logging.exception("Failed to apply LED config")

if __name__ == "__main__":
    main()
