import time
import board
import logging
import adafruit_pixelbuf
from adafruit_raspberry_pi5_neopixel_write import neopixel_write

PIN = board.D10 # GPIO 10 (MOSI)
LED_COUNT = 21

# Configure logging to both file and console
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
console_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(console_handler)

class WS2814_RGBW(adafruit_pixelbuf.PixelBuf):
    def __init__(self, pin, size, **kwargs):
        self._pin = pin
        super().__init__(size=size, byteorder="WRGB", **kwargs)

    def _transmit(self, buf):
        neopixel_write(self._pin, buf)

pixels = WS2814_RGBW(PIN, LED_COUNT, auto_write=True)

try:
    while True:
        for i in range(LED_COUNT):
            if i < 10:
                pixels[i] = (255, 0, 0, 0)  # RED
            else:
                pixels[i] = (0, 0, 255, 0)  # BLUE
        logging.info("show")
        pixels.show()
        time.sleep(2)
        # Turn off all LEDs
        pixels.fill((0, 0, 0, 0))
        time.sleep(1)
except KeyboardInterrupt:
    pixels.fill((0, 0, 0, 0))
