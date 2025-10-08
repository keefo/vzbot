# Sound/TTS for Klipper

Text-to-speech integration for Klipper 3D printer using Python.

## Features

- Multiple TTS engine support (pico2wave, espeak-ng, Piper)
- Audio normalization and volume boost with sox
- Flexible audio device selection
- Works from command line and Klipper G-code macros

## Installation

Run the setup script:

```bash
cd ~/vzbot/sound
chmod +x setup.sh
./setup.sh
```

This will:
- Install required system packages (pico2wave, espeak-ng, sox, alsa-utils)
- Add current user and klipper user to audio group
- Make speak.py executable
- Test audio output

## Usage

### From Command Line

```bash
./speak.py "Hello World"
```

### From Klipper

Add to your `printer.cfg` or `shell_command.cfg`:

```ini
[gcode_shell_command SPEAK_TEXT]
command = python3 /home/lianxu/vzbot/sound/speak.py
timeout = 5.0
verbose: True

[gcode_macro SPEAK]
gcode:
  RUN_SHELL_COMMAND CMD=SPEAK_TEXT PARAMS="{params.MSG|default('Hello World')}"
```

Then use in G-code:

```gcode
SPEAK MSG="Print started"
SPEAK MSG="Heating bed to 60 degrees"
```

## Configuration

### Environment Variables

- `DEVICE` - Audio device (default: auto-detect, fallback to "default")
- `LANG_TTS` - Language code (default: "en-US")
- `GAIN_DB` - Volume boost in dB (default: "8")
- `PIPER_MODEL` - Path to Piper TTS model (optional)

### Examples

```bash
# Use specific audio device
DEVICE=plughw:2,0 ./speak.py "Test"

# Change language
LANG_TTS=en-GB ./speak.py "Hello"

# Adjust volume boost
GAIN_DB=12 ./speak.py "Louder message"
```

### Finding Your Audio Device

```bash
aplay -L
```

Common devices:
- `default` - System default (recommended)
- `pulse` - PulseAudio
- `plughw:0,0` - First hardware device
- `plughw:2,0` - Third hardware device (like I2S DAC)

## Troubleshooting

### Check system status

```bash
./status.sh
```

### Test from command line first

```bash
./speak.py "Test message"
```

If it works from command line but not from Klipper:

1. **Check klipper user has audio permissions:**
   ```bash
   sudo usermod -a -G audio klipper
   sudo systemctl restart klipper
   ```

2. **Try different audio device:**
   ```ini
   [gcode_shell_command SPEAK_TEXT]
   command = sh -c 'DEVICE=default python3 /home/lianxu/vzbot/sound/speak.py "$@"' --
   ```

3. **Check Klipper logs:**
   ```bash
   tail -f ~/printer_data/logs/klippy.log
   ```

### No sound output

- Verify audio device: `aplay -L`
- Test audio: `speaker-test -t sine -f 1000 -l 1`
- Check volume: `alsamixer`

## Uninstallation

```bash
./remove.sh
```

Then remove the `[gcode_shell_command SPEAK_TEXT]` and `[gcode_macro SPEAK]` sections from your Klipper config.

## TTS Engines

The script tries these engines in order:

1. **Piper** (best quality, requires model file)
2. **pico2wave** (good quality, lightweight)
3. **espeak-ng** (robotic but fast)

Install Piper separately if desired: https://github.com/rhasspy/piper
