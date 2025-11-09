
# WS2814 RGBW LED Strip Controller (WLED-based)

This script controls WS2814 24V LED strip lights via **WLED over WiFi**. WS2814 are advanced 4-in-1 addressable LEDs featuring RGBW (Red, Green, Blue, White) color channels. The WS2814 is an evolution of the popular WS2812 series with several key improvements.

**Current Setup**: ESP32 WLED controller at `http://vzbot-wled.local`

https://www.aliexpress.com/item/1005004794429155.html?spm=a2g0o.order_list.order_list_main.314.73061802A57OPl#nav-specification

DC24V 5M 420LEDS, Black PCB, RGB WW IP67


## 📋 LED Specifications

| Parameter | Value |
|-----------|-------|
| **Type** | WS2814 RGB WW (4-in-1) |
| **Voltage** | 24V DC |
| **Form Factor** | 5050 SMD package |
| **Colors** | RGB + dedicated white channel |
| **Protocol** | Single-wire digital control (similar to WS2812) |
| **Connector** | 3-pin (Data, VCC, GND) |
| **Waterproofing** | IP30 (indoor), IP65 (water-resistant), IP67 (waterproof) |

## ⚡ Advantages of WS2814 vs WS2812

1. **Higher Voltage**: 24V operation reduces voltage drop and power loss over long runs
2. **True White**: Dedicated white channel produces pure white light (not RGB mixed white)
3. **Better Performance**: Improved color accuracy and brightness
4. **Efficiency**: Fewer power injection points needed for long strips
5. **Lower Current**: Reduced current draw per meter

## 🎯 Strip Layout (21 LEDs Total)

```
        Back (0-4)
           █████
Left    █          █    Right
(15-19) █          █    (5-9)
        █          █
           █████
        Front (10-14)
     
     Additional LED: 20
```

### Section Breakdown:
- **Back section**: LEDs 0-4 (5 LEDs)
  - Back Left: 0-1
  - Back Middle: 2
  - Back Right: 3-4
- **Right section**: LEDs 5-9 (5 LEDs)
- **Front section**: LEDs 10-14 (5 LEDs)
- **Left section**: LEDs 15-19 (5 LEDs)
- **Additional**: LED 20 (1 LED)

## ✨ Features

- 🎨 Individual LED control with RGBW color mixing via WLED
- 🌈 Predefined color patterns and WLED built-in animations
- 📍 Section-based lighting (back, front, left, right)
- 🎄 Rainbow and Christmas light effects (using WLED effects)
- 🔆 Configurable brightness control
- 📝 Comprehensive logging to file and console
- 🌐 WiFi-based control via ESP32 WLED controller
- 💪 Reliable hardware timing (no GPIO timing issues)
- 🔄 No keep-alive needed (WLED maintains state)

## 🏗️ Current Hardware Setup

**✅ Production Setup (Currently in use):**
```
Raspberry Pi 5 (WiFi) ←→ ESP32 WLED Controller ←→ WS2814 Strip
                            (vzbot-wled.local)         |
                                                       v
                                                  24V Power Supply
```

**Hardware Components:**
- **Controller**: ESP32 WLED board at `http://vzbot-wled.local`
- **LED Strip**: WS2814 RGBW, 21 LEDs, 24V DC
- **Power Supply**: 24V DC for LED strip
- **Communication**: WiFi (HTTP JSON API)
- **GPIO Pin**: GPIO 2 (on ESP32)
- **LED Configuration**: 
  - Type: `SK6812/WS2814 RGBW`
  - Color Order: `BRG`
  - Swap: `W & G`

## 📂 Project Structure

```
led/
├── set.py                  # Main control script (WLED-based)
├── wled_controller.py      # WLED HTTP API wrapper
├── led_service.py          # Service that monitors config changes
├── common.py               # Shared configuration
├── logs/                   # Log files
│   └── set.log
├── bak/                    # Backup of old GPIO-based code
│   ├── set.py.bak         # Old direct GPIO implementation
│   └── common.py.bak
└── readme.md              # This file

Config file location: ~/printer_data/config/led_config.ini
```

## 🔧 Hardware Setup

### ✅ Current Setup: WLED Controller (Recommended)

**You are using this setup!** This provides reliable control via WiFi HTTP API.

#### Hardware:
- ESP32 WLED Controller (`vzbot-wled.local`)
- WS2814 24V RGBW LED Strip (21 LEDs)
- 24V Power Supply

#### Wiring:
```
ESP32 WLED Board:
  GPIO 2 → WS2814 DATA
  GND → WS2814 GND (and 24V PSU GND)
  5V USB → 5V Power

24V Power Supply:
  24V → WS2814 VCC
  GND → WS2814 GND (and ESP32 GND)

Raspberry Pi 5:
  WiFi → ESP32 WLED (HTTP API)
```

#### WLED Configuration:
- **URL**: `http://vzbot-wled.local`
- **LED Type**: `SK6812/WS2814 RGBW` (4-channel)
- **LED Count**: `21`
- **GPIO**: `2`
- **Color Order**: `BRG` (Blue, Red, Green, White)
- **Swap**: `W & G` (swaps White and Green channels)

### 📦 Software Setup

#### 1. Install Dependencies:
```bash
cd ~/vzbot/led
pip install requests
```

#### 2. Configure LED Settings:

Create or edit `~/printer_data/config/led_config.ini`:
```ini
[led]
pattern = orangeteal
brightness = 0.5
white = 0
```

#### 3. Available Patterns:

| Pattern | Description |
|---------|-------------|
| `off` | Turn off all LEDs |
| `red`, `blue`, `green` | Solid colors |
| `yellow`, `purple`, `orange`, `pink` | More solid colors |
| `white` | Full white (RGB + W channel) |
| `sunset` | Orange-red color |
| `orangeteal` | Back/Right: Orange, Front/Left: Teal |
| `demo` | White back/front, Red right, Blue left |
| `backonly` | Only back LEDs white |
| `rainbow` | Rainbow animation (WLED effect) |
| `xmas` | Christmas lights (WLED effect) |
| `0xRRGGBB` | Custom hex color (e.g., `0xFF5500`) |

#### 4. Run Manually:
```bash
cd ~/vzbot/led
python3 set.py
```

LEDs will update immediately and script exits (WLED maintains state).

#### 5. Run as Service:

Use `led_service.py` to automatically apply changes when config file is modified:
```bash
cd ~/vzbot/led
python3 led_service.py &
```

The service monitors `~/printer_data/config/led_config.ini` and restarts `set.py` whenever you change the pattern or brightness.

### 🔄 How It Works

```
Config File → led_service.py monitors → Detects change → Runs set.py → 
WLED HTTP API → ESP32 → WS2814 LEDs
```

**Key advantages over old GPIO method:**
- ✅ **Reliable timing**: Hardware-based, no glitches
- ✅ **No keep-alive needed**: WLED maintains LED state
- ✅ **WiFi control**: No wiring between Pi and ESP32
- ✅ **Web interface**: Manual control at `http://vzbot-wled.local`
- ✅ **Built-in effects**: 100+ animations in WLED
- ✅ **Persistent state**: LEDs stay on even if Pi reboots

---

### 📚 Alternative Setup: Direct GPIO Control (Legacy - Not Recommended)

**⚠️ This method is deprecated due to timing reliability issues on Raspberry Pi 5.**

Old GPIO-based code is backed up in `bak/` folder for reference.

#### Why WLED is Better:

| Feature | GPIO (Old) | WLED (Current) |
|---------|------------|----------------|
| Reliability | ⚠️ Timing issues | ✅ Perfect |
| Keep-alive | ❌ Required | ✅ Not needed |
| Setup | Complex | Simple |
| Web UI | ❌ None | ✅ Built-in |
| Effects | Manual code | 100+ built-in |
| Recovery | ❌ Fails on crash | ✅ Maintains state |

---

### 📚 Additional Information: Commercial LED Controllers

While WLED is recommended and you're already using it successfully, here are other options for reference:

#### WLED Controller Options:
- **Pre-built boards**: QuinLED-Dig-Uno, SP108E, SP501E
- **DIY**: Any ESP32 + level shifter + WLED firmware
- **Your board**: ESP32 WLED with microphone + UART
  - Supports music reactive effects
  - Optional serial control via UART
  - WiFi control (recommended method)

#### Other Controller Types:
- **SPI-based**: Adafruit NeoPixel Pi Hat (hardware SPI)
- **Standalone**: QuinLED, dig-uno (industrial reliability)

For your setup, WiFi control is the best approach - no additional wiring needed between Pi and ESP32.

---

## ⚙️ Configuration Options

Edit `~/printer_data/config/led_config.ini`:

```ini
[led]
pattern = orangeteal    # Pattern name (see below)
brightness = 0.5        # 0.0 to 1.0 (0% to 100%)
white = 0              # Extra white channel boost (0-255)
```

### Available Patterns:

| Pattern | Description | Example |
|---------|-------------|---------|
| `off` | Turn off all LEDs | All black |
| `red` | Solid red | Heating |
| `blue` | Solid blue | Cooling |
| `green` | Solid green | Ready |
| `yellow` | Solid yellow | Warning |
| `purple` | Solid purple | Pause |
| `orange` | Solid orange | Standby |
| `pink` | Solid pink | Custom |
| `white` | Full white (RGB + W) | Maximum brightness |
| `sunset` | Orange-red color | Warm light |
| `orangeteal` | Back/Right: Orange<br>Front/Left: Teal | Split color theme |
| `demo` | Back/Front: White<br>Right: Red<br>Left: Blue | Demo pattern |
| `backonly` | Only back LEDs white<br>All others off | Rear illumination |
| `rainbow` | Rainbow animation | WLED effect #9 |
| `xmas` | Christmas lights | WLED effect #47 |
| `0xRRGGBB` | Custom hex color | `0xFF5500` = orange |

### Pattern Details:

#### Solid Colors:
Set entire strip to one color. WLED maintains state - no keep-alive needed.

#### Segment Patterns (`orangeteal`, `demo`, `backonly`):
Send multiple segments with different colors to WLED in one API call. Each segment is configured with start/stop LED indices.

#### Animations (`rainbow`, `xmas`):
Use WLED's built-in effects:
- `rainbow`: Effect ID 9, smooth color cycle
- `xmas`: Effect ID 47, twinkling red/green

#### Custom Colors:
Use hex format: `pattern = 0xFF5500` for custom RGB color (white channel = 0).

### Brightness Control:

```ini
brightness = 0.5   # 50% brightness
```

- Range: `0.0` to `1.0` (0% to 100%)
- Affects all colors/patterns equally
- Converted to WLED brightness (0-255)

### White Channel:

```ini
white = 0         # No extra white
white = 128       # Half white boost
white = 255       # Full white boost
```

- Only applies to solid color patterns
- Adds pure white LED channel (WS2814 4th channel)
- Useful for brighter, cooler whites

---

## 🖥️ Manual Control

### Command Line:
```bash
# Edit config
nano ~/printer_data/config/led_config.ini

# Apply changes
cd ~/vzbot/led
python3 set.py
```

### WLED Web Interface:
Open `http://vzbot-wled.local` in browser for manual control:
- On/Off toggle
- Brightness slider
- Color picker
- 100+ built-in effects
- Segment configuration
- Presets and playlists

---

## 🔄 Service Mode

Run `led_service.py` to automatically apply changes when config file is modified:

```bash
cd ~/vzbot/led
python3 led_service.py &
```

The service:
1. Watches `~/printer_data/config/led_config.ini`
2. Detects file modifications
3. Runs `set.py` to apply new settings
4. Logs to `logs/led_service.log`

**Add to systemd** (optional):
```bash
sudo nano /etc/systemd/system/led-service.service
```

```ini
[Unit]
Description=LED Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/vzbot/led
ExecStart=/usr/bin/python3 /home/pi/vzbot/led/led_service.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable led-service
sudo systemctl start led-service
```

---

## 🐛 Troubleshooting

### LEDs Not Responding:

**Check WLED connectivity:**
```bash
ping vzbot-wled.local
# or
curl http://vzbot-wled.local/json/info
```

**If hostname not resolving:**
```bash
# Find WLED IP via router DHCP table
# Or scan network:
nmap -p 80 192.168.0.0/24 | grep -B 4 "open"

# Update set.py and wled_controller.py with IP:
WLED_IP = "192.168.0.190"  # Replace with your IP
```

**Check WLED web interface:**
- Open `http://vzbot-wled.local`
- Verify LED count: 21
- Verify GPIO: 2
- Verify type: SK6812/WS2814 RGBW
- Check color order: BRG
- Check swap: W & G enabled

### Wrong Colors:

If colors are incorrect, adjust WLED configuration:
1. Open `http://vzbot-wled.local`
2. Config → LED Preferences
3. Try different color orders: `RGB`, `RBG`, `GRB`, `GBR`, `BRG`, `BGR`
4. Try W channel swaps: `None`, `W & G`, `W & R`, `W & B`

**For WS2814 RGBW:** `BRG` + `W & G swap` is correct.

### Script Hangs:

If `set.py` doesn't exit:
```bash
# Check logs:
tail -f ~/vzbot/led/logs/set.log

# Kill if stuck:
pkill -f set.py

# Test connectivity:
curl -X POST http://vzbot-wled.local/json/state -H "Content-Type: application/json" -d '{"on":true,"bri":128,"seg":[{"col":[[255,0,0,0]]}]}'
```

### Config Not Applying:

If changes to `led_config.ini` don't take effect:
```bash
# Run manually:
cd ~/vzbot/led
python3 set.py

# Check config file syntax:
cat ~/printer_data/config/led_config.ini

# Verify led_service.py is running:
ps aux | grep led_service
```

### Power Issues:

**LEDs dim or flickering:**
- Check 24V power supply capacity (21 LEDs × 0.3W = ~7W minimum)
- Verify all ground connections: ESP32 GND, LED GND, PSU GND all connected
- Check voltage at LED strip: should be 23-25V

**First LED works, rest don't:**
- Data line not connected
- Wrong GPIO pin in WLED config
- Level shifter issue (if using one)

### Network Issues:

**WLED not accessible from Pi:**
```bash
# Check Pi WiFi:
iwconfig

# Check routing:
ip route

# Try IP instead of hostname:
curl http://192.168.0.190/json/info
```

**Intermittent connectivity:**
- Check WiFi signal strength at WLED location
- Assign static IP in router DHCP settings
- Update WLED firmware to latest version

---

## 📝 Logs

View recent LED operations:
```bash
tail -f ~/vzbot/led/logs/set.log
```

Log format:
```
2024-01-15 10:30:45 - INFO - LED pattern set to: orangeteal
2024-01-15 10:30:45 - INFO - Brightness: 0.5
2024-01-15 10:30:45 - INFO - White boost: 0
2024-01-15 10:30:46 - INFO - LEDs updated successfully
```

---

## 🔧 Advanced Usage

### Custom Python Scripts:

Use `wled_controller.py` directly:

```python
from wled_controller import WLEDController

# Initialize
wled = WLEDController("vzbot-wled.local")

# Solid color (red)
wled.set_color(255, 0, 0, w=0, brightness=128)

# Multiple segments
segments = [
    {"start": 0, "stop": 5, "col": [[255, 0, 0, 0]]},      # Red
    {"start": 6, "stop": 10, "col": [[0, 255, 0, 0]]},     # Green  
    {"start": 11, "stop": 20, "col": [[0, 0, 255, 0]]}     # Blue
]
wled.set_segment_colors(segments)

# Use WLED effect
wled.set_effect(effect_id=9, speed=128, intensity=128)  # Rainbow

# Turn off
wled.turn_off()
```

### Integration with Klipper Macros:

Add to `printer.cfg`:

```gcode
[gcode_shell_command set_led]
command: python3 /home/pi/vzbot/led/set.py
timeout: 5.0
verbose: True

[gcode_macro SET_LED_PATTERN]
gcode:
    {% set pattern = params.PATTERN|default("off")|lower %}
    {% set brightness = params.BRIGHTNESS|default(0.5)|float %}
    
    # Update config file
    RUN_SHELL_COMMAND CMD=update_led_config PARAMS="'{pattern}' {brightness}"
    
    # Wait for service to apply or run directly
    G4 P500  # Wait 500ms
    
    M118 LED pattern set to {pattern}

[gcode_macro LED_HEATING]
gcode:
    SET_LED_PATTERN PATTERN=red BRIGHTNESS=0.7

[gcode_macro LED_READY]
gcode:
    SET_LED_PATTERN PATTERN=green BRIGHTNESS=0.5

[gcode_macro LED_PRINTING]
gcode:
    SET_LED_PATTERN PATTERN=orangeteal BRIGHTNESS=0.8

[gcode_macro LED_DONE]
gcode:
    SET_LED_PATTERN PATTERN=rainbow BRIGHTNESS=1.0
```

### API Reference:

**WLED JSON API Endpoints:**
- `/json/state` - Control LEDs
- `/json/info` - Get device info
- `/json/effects` - List effects
- `/json/palettes` - List color palettes

**set.py patterns:**
- Solid: `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `white`, `sunset`
- Segments: `orangeteal`, `demo`, `backonly`
- Animations: `rainbow`, `xmas`
- Custom: `0xRRGGBB` (hex format)
- Off: `off`

---

## 🔗 Resources

- **WLED Official**: https://kno.wled.ge/
- **WLED GitHub**: https://github.com/Aircoookie/WLED
- **WLED API Docs**: https://kno.wled.ge/interfaces/json-api/
- **WS2814 Datasheet**: Search "WS2814 RGBW LED protocol"
- **This Project**: `/Volumes/2T_C/3dprints/vzbot/led/`

---

## 📜 License

This project is provided as-is for personal use. WLED is licensed under MIT License.

---

## 🎉 Credits

- **WLED Firmware**: Aircoookie and contributors
- **Hardware**: ESP32 WLED controller
- **Integration**: Custom Python scripts for Klipper/printer control

---

**Enjoy your RGBW LED lighting! 🌈**
