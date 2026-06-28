# 2026-06-27 — Super 8 Pro: USB serial → USB-to-CAN bridge

**Goal:** Migrate the Super 8 Pro (H723) from USB serial to USB-to-CAN bridge mode in
preparation for the SHT36 V3 Max CAN toolhead.

## Pre-change
- **Main board**: Fly Super 8 Pro (STM32H723) connected to the Pi over USB-C and
  enumerating as a USB serial Klipper device (`1d50:614e`, serial
  `usb-Klipper_stm32h723xx_4A0018001651313338343730`).
- **printer.cfg**: `[mcu]` used `serial: /dev/serial/by-id/usb-Klipper_stm32h723xx_...`
  (plain USB serial, no CAN).
- **CAN bus**: none. The Pi had **no `can0`** interface and no USB CAN adapter present.
- **Bootloader**: board already had a Katapult + Klipper flash layout (Klipper app at
  `0x08020000`), though this was not yet known/used for CAN.
- **Toolhead**: SHT36 V3 Max acquired but not yet on the bus. It had Katapult flashed
  (via RP2 boot mode) but no Klipper, and there was no CAN path to reach it.
- **Moonraker**: no `katapult` entry in the update manager.
- **Motivation**: the new SHT36 V3 Max is a CAN toolhead, so the main board needed to
  provide a CAN bus. Chosen approach: put the Super 8 Pro into USB-to-CAN bridge mode
  (no extra UTOC adapter hardware required).

## Post-change
- Super 8 Pro now runs Klipper in USB-to-CAN bridge mode.
- Pi talks to the main MCU over CAN (`canbus_uuid: 538e6d5fb457`) tunneled through the USB-C cable.
- `can0` is persistent at 1 Mbit; Klipper reconnected successfully.
- SHT36 toolhead detected on the bus (`85a1452bd027`), still in Katapult — Klipper flash over CAN pending.

## Steps
1. Attempted SD-card flashing first; discovered the Super 8 Pro H723 has **no SD-card
   bootloader** (`firmware.bin` was never consumed). Confirmed against Mellow's official
   `fly_super8_pro/flash.md`, which documents DFU flashing only.
2. Backed up the board's existing firmware marker (`FLY.CUR.2024-07-12.bin`) into
   `doc/firmware_backup/super8pro_h723/` before making changes.
3. Built the USB-to-CAN bridge Klipper firmware on the Pi (`v0.13.0-699-gc707dd19`,
   app address `0x08020000`, 1 Mbit CAN, USB PA11/PA12, CAN PB8/PB9).
4. Entered DFU (BT0/3.3V jumper) and flashed the Katapult bootloader via `dfu-util`.
5. Discovered the board already had a Katapult + Klipper layout, so used
   `flashtool.py -r` to drop the running Klipper into Katapult, then flashed the
   bridge firmware over USB. Verified OK.
6. Board re-enumerated as a `gs_usb` CAN adapter (`1d50:606f`); created the persistent
   `can0` systemd service (1 Mbit).
7. Switched `printer.cfg` `[mcu]` from serial to `canbus_uuid: 538e6d5fb457`; Klipper
   reconnected to the main MCU over CAN successfully.
8. Registered `katapult` in Moonraker's update manager.
9. CAN scan found two nodes: main board `538e6d5fb457` (Klipper) and SHT36 toolhead
   `85a1452bd027` (Katapult — Klipper flash over CAN still pending).

## Key commands
```bash
# DFU flash Katapult bootloader
dfu-util -a 0 -d 0483:df11 --dfuse-address 0x08000000:leave -D ~/katapult/out/katapult.bin

# Drop running Klipper into Katapult, then flash bridge firmware
python3 ~/katapult/scripts/flashtool.py -d <klipper-by-id> -r
python3 ~/katapult/scripts/flashtool.py -d <katapult-by-id> -f ~/klipper/out/klipper.bin

# List CAN devices
python3 ~/katapult/scripts/flashtool.py -i can0 -q
```

## Follow-ups
- Build and flash SHT36 RP2040 Klipper firmware over CAN (`-u 85a1452bd027`).
- Add `[mcu SHT36]` section and migrate toolhead pins (extruder, hotend heater,
  thermistor, part fan, TMC2209, accelerometer).
