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

    def set_color(self, r, g, b, w=0, brightness=128, start=0, stop=21):
        """
        Set solid color across all LEDs (RGBW 4-channel)
        r, g, b = RGB color values (0-255)
        w = White channel value (0-255)
        brightness = Overall brightness (0-255)
        start = Starting LED index (default 0)
        stop = Ending LED index (default 21)
        """
        try:
            response = requests.post(f"{self.base_url}/state", json={
                "on": True,
                "seg": [{
                    "id": 0,
                    "start": start,
                    "stop": stop,
                    "fx": 0,  # Solid effect
                    "col": [[r, g, b, w]],  # RGBW (4 values)
                    "bri": brightness
                }]
            }, timeout=2)
            return response.ok
        except Exception as e:
            logging.error(f"Failed to set color: {e}")
            return False

    def set_segment_colors(self, segments, brightness=None):
        """
        Set different colors for different LED segments
        NOTE: This now uses segment ID 0 only and just updates colors,
        not creating new segments
        """
        try:
            # Use only segment 0, update just the color
            # Take the first segment's color as the main color
            if segments:
                first_seg = segments[0]
                seg_config = {
                    "id": 0,
                    "col": [first_seg["col"]]
                }
                if brightness is not None:
                    seg_config["bri"] = brightness

                response = requests.post(f"{self.base_url}/state", json={
                    "on": True,
                    "seg": [seg_config]
                }, timeout=2)
                return response.ok
            return False
        except Exception as e:
            logging.error(f"Failed to set segments: {e}")
            return False

    def set_individual_leds(self, led_colors, brightness=None):
        """
        Set individual LED colors using WLED's /json/state API
        led_colors: list of (r, g, b, w) tuples for each LED
        """
        try:
            # First, unfreeze the segment
            requests.post(f"{self.base_url}/state", json={
                "seg": [{"id": 0, "frz": False}]
            }, timeout=2)
            
            # Build the individual LED data
            # WLED format: {"seg":[{"id":0,"i":[index,r,g,b,w, index,r,g,b,w, ...]}]}
            led_data = []
            for idx, (r, g, b, w) in enumerate(led_colors):
                led_data.extend([idx, r, g, b, w])

            seg_config = {
                "id": 0,
                "i": led_data,
                "fx": 0  # Set effect to Solid (0) to use our colors
            }
            if brightness is not None:
                seg_config["bri"] = brightness

            payload = {
                "on": True,
                "seg": [seg_config]
            }
            
            logging.debug(f"Sending to WLED: {len(led_data)} LED values, brightness={brightness}, fx=0")
            
            response = requests.post(f"{self.base_url}/state", json=payload, timeout=2)
            return response.ok
        except Exception as e:
            logging.error(f"Failed to set individual LEDs: {e}")
            return False

    def reset_to_single_segment(self, start=0, stop=21):
        """
        Reset WLED to use a single segment covering all LEDs
        Call this after complex patterns to clean up extra segments
        """
        try:
            response = requests.post(f"{self.base_url}/state", json={
                "on": True,
                "mainseg": 0,
                "seg": [
                    {
                        "id": 0,
                        "start": start,
                        "stop": stop,
                        "on": True
                    }
                ]
            }, timeout=2)
            return response.ok
        except Exception as e:
            logging.error(f"Failed to reset segments: {e}")
            return False

    def set_effect(self, effect_id=0, speed=128, intensity=128, start=0, stop=21):
        """
        Set WLED built-in effect

        Args:
            effect_id: Effect number (0=Solid, 1=Blink, 9=Rainbow, etc.)
            speed: Effect speed (0-255)
            intensity: Effect intensity (0-255)
            start: Starting LED index (default 0)
            stop: Ending LED index (default 21)
        
        Note: start and stop are REQUIRED for effects to work properly on WLED
        """
        try:
            seg_config = {
                "id": 0,
                "start": start,
                "stop": stop,
                "fx": effect_id,  # 0=Solid, 1=Blink, 9=Rainbow, etc.
                "sx": speed,      # 0-255
                "ix": intensity   # 0-255
            }

            response = requests.post(f"{self.base_url}/state", json={
                "on": True,
                "seg": [seg_config]
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
