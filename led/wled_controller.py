import requests
import logging
from common import WLED_IP


class WLEDController:
    def __init__(self, ip=None):
        """
        Initialize WLED controller

        Args:
            ip: WLED controller hostname or IP address.
                If None, uses WLED_IP from common.py
        """
        self.ip = ip or WLED_IP
        self.base_url = f"http://{self.ip}/json"

    def set_color(self, r, g, b, w=0, brightness=128):
        """
        Set solid color across all LEDs (RGBW 4-channel)
        r, g, b = RGB color values (0-255)
        w = White channel value (0-255)
        brightness = Overall brightness (0-255)
        """
        try:
            response = requests.post(f"{self.base_url}/state", json={
                "on": True,
                "bri": brightness,  # 0-255
                "seg": [{
                    "col": [[r, g, b, w]]  # RGBW (4 values)
                }]
            }, timeout=2)
            return response.ok
        except Exception as e:
            logging.error(f"Failed to set color: {e}")
            return False

    def set_segment_colors(self, segments):
        """
        Set different colors for different LED segments
        segments = [
            {"start": 0, "stop": 5, "col": [255, 0, 0, 0]},   # Back: red
            {"start": 5, "stop": 10, "col": [0, 255, 0, 0]},  # Right: green
        ]
        """
        try:
            seg_list = []
            for i, seg in enumerate(segments):
                seg_list.append({
                    "id": i,
                    "start": seg["start"],
                    "stop": seg["stop"],
                    "col": [seg["col"]]
                })

            response = requests.post(f"{self.base_url}/state", json={
                "on": True,
                "seg": seg_list
            }, timeout=2)
            return response.ok
        except Exception as e:
            logging.error(f"Failed to set segments: {e}")
            return False

    def set_effect(self, effect_id=0, speed=128, intensity=128):
        """Set WLED built-in effect"""
        try:
            response = requests.post(f"{self.base_url}/state", json={
                "on": True,
                "seg": [{
                    "fx": effect_id,  # 0=Solid, 1=Blink, 9=Rainbow, etc.
                    "sx": speed,      # 0-255
                    "ix": intensity   # 0-255
                }]
            }, timeout=2)
            return response.ok
        except Exception as e:
            logging.error(f"Failed to set effect: {e}")
            return False

    def turn_off(self):
        """Turn off all LEDs"""
        try:
            response = requests.post(f"{self.base_url}/state", json={
                "on": False
            }, timeout=2)
            return response.ok
        except Exception as e:
            logging.error(f"Failed to turn off: {e}")
            return False
