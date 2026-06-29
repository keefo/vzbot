# 2026-06-29 — Super8 bridge PF8/PF7 startup quieting

## Goal
Stop Super8 `PF8` print cooling fan and `PF7` heatsink pump outputs from briefly turning on
during `FIRMWARE_RESTART` after the SHT36 migration.

## Pre-change
- Print cooling fan still physically connected to the Super8 Pro `PF8` fan output.
- Heatsink pump still physically connected to the Super8 Pro `PF7` heater/MOSFET output.
- `new_config/printer.cfg` already had `[fan] pin: PF8` and `shutdown_speed: 0`, so Klipper
  commanded the fan off after reconnect.
- `new_config/printer.cfg` also had `[temperature_fan heatsink_pump] pin: PF7` and
  `shutdown_speed: 0.0`, so Klipper commanded the pump off after reconnect.
- The running USB-to-CAN bridge firmware initially had no initial pin override for these outputs,
  leaving a reset window where the MOSFETs could turn on before Klipper reconfigured the pins.
- Existing repo `klipper-kconfigs/super8pro.config` had `CONFIG_INITIAL_PINS=" !PF8"` but was
  an older plain-USB Super8 config, not the active USB-to-CAN bridge config.

## Post-change
- Super8 Pro H723 USB-to-CAN bridge firmware rebuilt and flashed with:
  `CONFIG_INITIAL_PINS="!PF8,!PF7"`.
- Klipper log confirms the running main MCU reports `INITIAL_PINS=!PF8,!PF7` and
  `CANBUS_BRIDGE=1`.
- Klipper restarted successfully; `mcu`, `sht36`, and `rpi` all configured cleanly.
- Acoustic result still needs user confirmation at the printer during the next
  `FIRMWARE_RESTART`.

## Steps
1. Added `klipper-kconfigs/super8pro_usb2can_pf8-safe.config` as a dedicated Super8 Pro H723
  USB-to-CAN bridge build config, first with `CONFIG_INITIAL_PINS="!PF8"`, then updated to
  `CONFIG_INITIAL_PINS="!PF8,!PF7"` after the heatsink pump showed the same restart behavior.
2. Backed up the Pi-side Klipper build state to
   `~/firmware_backups/super8_pf8_startup_20260629-002030/`.
3. Loaded the corrected bridge config into `~/klipper/.config`, ran `make olddefconfig`, and
   rebuilt Klipper firmware.
4. Stopped Klipper, requested Katapult over CAN for main MCU UUID `538e6d5fb457`, and flashed
   `~/klipper/out/klipper.bin` over the Katapult USB serial device.
5. Started Klipper again and verified the latest `klippy.log` showed all MCUs configured.
6. Repeated the same build/flash cycle for the `PF8,PF7` firmware; Pi-side pre-build backup:
  `~/firmware_backups/super8_pf8_pf7_startup_20260629-002710/`.

## Key commands
```bash
# Pi-side build verification
cd ~/klipper
make olddefconfig
grep -E 'CONFIG_USBCANBUS=|CONFIG_STM32_USBCANBUS_PA11_PA12=|CONFIG_STM32_CANBUS_PB8_PB9=|CONFIG_INITIAL_PINS=' .config
make -j4

# Enter Katapult and flash
sudo systemctl stop klipper
python3 ~/katapult/scripts/flashtool.py -i can0 -u 538e6d5fb457 -r
python3 ~/katapult/scripts/flashtool.py -d /dev/ttyACM0 -f ~/klipper/out/klipper.bin

# Restore runtime
sudo ip link set can0 up type can bitrate 1000000
sudo ip link set can0 txqueuelen 128
sudo systemctl start klipper
```

## Follow-ups
- User should run or observe one `FIRMWARE_RESTART` and confirm the PF8 print cooling fan and
  PF7 heatsink pump no longer turn on during the reset window.
- If a brief blip remains, the next suspect is hardware-level MOSFET/gate pull behavior; add an
  external pull or move the affected output to a connector with a known quiet reset state.
- Future Super8 bridge firmware rebuilds should use
  `klipper-kconfigs/super8pro_usb2can_pf8-safe.config`, not the older plain-USB
  `klipper-kconfigs/super8pro.config`.

Firmware identity:
- Current repo artifact: `doc/firmware_backup/super8pro_h723/klipper_usb2can_pf8-pf7-safe.bin`
- Previous PF8-only artifact: `doc/firmware_backup/super8pro_h723/klipper_usb2can_pf8-safe.bin`
- Klipper version: `v0.13.0-699-gc707dd19`
- Current SHA256: `01ebeead4d2cb5c81c28231dd9390f9e95a6c870c689729590a2b2c3bdbd7860`
- Current SHA1: `87eece00ad789da3abacd0bba0e9fca3e263b055`