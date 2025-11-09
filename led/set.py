import os
import configparser
import logging
import time
from wled_controller import WLEDController
from common import LOG_DIR, CONFIG_FILE, WLED_IP, LED_COUNT

LOG_FILE = os.path.join(LOG_DIR, "set.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="[%(asctime)s] %(levelname)s: %(message)s",
)


class WS2814_RGBW_WLED:
    """WLED-based LED controller - replaces direct GPIO control"""

    def __init__(self, wled_ip, size, brightness=0.3, **kwargs):
        self.wled = WLEDController(wled_ip)
        self.size = size
        self.brightness = int(brightness * 255)  # Convert 0.0-1.0 to 0-255
        self.pixels = [(0, 0, 0, 0)] * size  # Local state buffer

    def __setitem__(self, index, color):
        """Set pixel color at index"""
        self.pixels[index] = color

    def __getitem__(self, index):
        """Get pixel color at index"""
        return self.pixels[index]

    def __len__(self):
        return self.size

    def fill(self, color):
        """Fill all LEDs with one color"""
        for i in range(self.size):
            self.pixels[i] = color
        self.show()

    def show(self):
        """Send all pixel data to WLED (solid color mode)"""
        if not self.pixels:
            return
        # Use the first pixel color as solid color for simplicity
        r, g, b, w = self.pixels[0]
        self.wled.set_color(r, g, b, w, brightness=self.brightness)

    def set_back(self, color):
        for i in range(0, 5):
            self.pixels[i] = color

    def set_back_left(self, color):
        for i in range(0, 2):
            self.pixels[i] = color

    def set_back_middle(self, color):
        for i in range(2, 3):
            self.pixels[i] = color

    def set_back_right(self, color):
        for i in range(3, 5):
            self.pixels[i] = color

    def set_right(self, color):
        for i in range(5, 10):
            self.pixels[i] = color

    def set_front(self, color):
        for i in range(10, 15):
            self.pixels[i] = color

    def set_left(self, color):
        for i in range(15, 20):
            self.pixels[i] = color

    def show_segments(self):
        """Send segment-based colors to WLED (for orangeteal, demo, backonly patterns)"""
        # Build segments list from pixel buffer
        segments = []
        current_color = self.pixels[0]
        start_idx = 0

        for i in range(1, len(self.pixels)):
            if self.pixels[i] != current_color:
                # End current segment
                r, g, b, w = current_color
                segments.append({"start": start_idx, "stop": i, "col": [r, g, b, w]})
                # Start new segment
                current_color = self.pixels[i]
                start_idx = i

        # Add final segment
        r, g, b, w = current_color
        segments.append({"start": start_idx, "stop": len(self.pixels), "col": [r, g, b, w]})

        # Send to WLED
        self.wled.set_segment_colors(segments)

    def animate_rainbow(self, delay=0.5):
        """Use WLED built-in rainbow effect"""
        logging.info("Starting rainbow animation via WLED effect")
        self.wled.set_effect(effect_id=9, speed=128)  # Effect 9 = Rainbow
        # Keep running to maintain compatibility with old interface
        while True:
            time.sleep(60)  # Just sleep, WLED handles the animation

    def animate_xmas(self, delay=0.5):
        """Use WLED built-in Christmas effect"""
        logging.info("Starting Christmas animation via WLED effect")
        self.wled.set_effect(effect_id=47, speed=128)  # Effect 47 = Christmas
        # Keep running to maintain compatibility with old interface
        while True:
            time.sleep(60)  # Just sleep, WLED handles the animation

    def animate_keep_alive(self):
        """
        No keep-alive needed with WLED!
        WLED maintains state automatically, so this just sleeps forever
        """
        logging.info("Keep-alive not needed with WLED - sleeping")
        while True:
            time.sleep(3600)  # Sleep 1 hour


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
    except Exception:
        logging.exception("Failed to parse LED config")
        return

    r = 0
    g = 0
    b = 0
    w = white

    logging.info(f"Setting LEDs to pattern={pattern}")
    # help convert pattern to r, g, b, w
    # if pattern start with 0x, it is a hex color
    # if pattern is red, blue, green, yellow, purple, orange, pink, brown,
    # gray, black, white, cyan, magenta, lime, maroon, navy, olive, purple,
    # teal, or violet, it is a color
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
        r = 253
        g = 89
        b = 1
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
    elif pattern == "orangeteal":
        try:
            pixels = WS2814_RGBW_WLED(WLED_IP, LED_COUNT, brightness=brightness)
            # Set color segments
            orange = (253, 89, 1, 0)
            teal = (36, 158, 160, 0)
            pixels.set_back(orange)
            pixels.set_right(orange)
            pixels.set_front(teal)
            pixels.set_left(teal)
            pixels.show_segments()  # Use segment-based update
            logging.info("LEDs updated successfully.")
            pixels.animate_keep_alive()
        except Exception:
            logging.exception("Failed to apply LED config")
        return
    elif pattern == "demo":
        try:
            pixels = WS2814_RGBW_WLED(WLED_IP, LED_COUNT, brightness=brightness)
            # Set color segments
            pixels.set_back((255, 255, 255, 255))
            pixels.set_right((255, 0, 0, 20))
            pixels.set_front((255, 255, 255, 255))
            pixels.set_left((0, 0, 255, 20))
            pixels.show_segments()  # Use segment-based update
            logging.info("LEDs updated successfully.")
            pixels.animate_keep_alive()
        except Exception:
            logging.exception("Failed to apply LED config")
        return
    elif pattern == "rainbow":
        try:
            pixels = WS2814_RGBW_WLED(WLED_IP, LED_COUNT, brightness=brightness)
            pixels.animate_rainbow()
            logging.info("LEDs updated successfully.")
        except Exception:
            logging.exception("Failed to apply LED config")
        return
    elif pattern == "xmas":
        try:
            pixels = WS2814_RGBW_WLED(WLED_IP, LED_COUNT, brightness=brightness)
            pixels.animate_xmas()
            logging.info("LEDs updated successfully.")
        except Exception:
            logging.exception("Failed to apply LED config")
        return
    elif pattern == "backonly":
        try:
            pixels = WS2814_RGBW_WLED(WLED_IP, LED_COUNT, brightness=brightness)
            pixels.set_back((255, 255, 255, 255))
            pixels.set_right((0, 0, 0, 0))
            pixels.set_front((0, 0, 0, 0))
            pixels.set_left((0, 0, 0, 0))
            pixels.show_segments()  # Use segment-based update
            logging.info("LEDs updated successfully.")
            pixels.animate_keep_alive()
        except Exception:
            logging.exception("Failed to apply LED config")
        return

    logging.info(f"Setting LEDs to pattern={pattern} white={white} brightness {brightness}")

    try:
        pixels = WS2814_RGBW_WLED(WLED_IP, LED_COUNT, brightness=brightness)
        pixels.fill((r, g, b, w))
        logging.info("LEDs updated successfully.")
        # No need to keep alive for solid colors - WLED maintains state
        # Just exit after setting the color
    except Exception:
        logging.exception("Failed to apply LED config")


if __name__ == "__main__":
    main()
