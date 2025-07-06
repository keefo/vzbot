import time
import board
import adafruit_pixelbuf
from adafruit_raspberry_pi5_neopixel_write import neopixel_write

NUM_LEDS = 20
PIN = board.D10  # GPIO10

class SK6812_RGBW(adafruit_pixelbuf.PixelBuf):
    def __init__(self, pin, size, **kwargs):
        self._pin = pin
        super().__init__(size=size, byteorder="WRGB", **kwargs)

    def _transmit(self, buf):
        neopixel_write(self._pin, buf)

pixels = SK6812_RGBW(PIN, NUM_LEDS, auto_write=True)

try:
    while True:
        for i in range(NUM_LEDS):
            if i < 10:
                pixels[i] = (255, 0, 0, 0)  # RED
            else:
                pixels[i] = (0, 0, 255, 0)  # BLUE
        pixels.show()
        time.sleep(2)

        # Turn off all LEDs
        pixels.fill((0, 0, 0, 0))
        time.sleep(1)
except KeyboardInterrupt:
    pixels.fill((0, 0, 0, 0))


# try:
#     while True:
#         pixels.fill((255, 0, 0, 0))  # RED only
#         time.sleep(1)
#         pixels.fill((0, 255, 0, 0))  # GREEN
#         time.sleep(1)
#         pixels.fill((0, 0, 255, 0))  # BLUE
#         time.sleep(1)
#         pixels.fill((0, 0, 0, 255))  # WHITE
#         time.sleep(1)
#         pixels.fill((0, 0, 0, 0))  # OFF
#         time.sleep(1)
# except KeyboardInterrupt:
#     pixels.fill((0, 0, 0, 0))
