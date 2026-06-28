# SHT36 V3 Max Integration Guide

- [Official Docs (intro)](https://mellow.klipper.cn/#/board/fly_sht36_v3_max/intro)
- [Official Pinout](https://mellow.klipper.cn/#/board/fly_sht36_v3_max/pinout)

---

## Step 0 — Choose connection method

The SHT36 V3 Max supports **CAN bus** or **USB**. CAN is strongly recommended for a toolhead (clean wiring, 4 wires only: 24V, GND, CANH, CANL).

Your Pi 5 doesn't have native CAN, so you need a **USB-CAN bridge**. Common choices:
- **Mellow UTOC-1/3** (Mellow's own, works well with their boards)
- **Waveshare USB-CAN adapter**
- Configure the **Fly Super 8 itself as a USB-CAN bridge** (saves buying extra hardware)

---

## Step 1 — Flash Katapult (bootloader) to SHT36

Katapult (formerly CANBoot) lets you re-flash Klipper over CAN without physical access.

Official Mellow notes for SHT36 V3:
- SHT36 V3 is RP2040-based.
- It is preloaded with Katapult/CAN boot support from factory (default CAN speed: 1M).
- Enter bootloader by holding BOOT while plugging Type-C USB.
- In boot mode, `lsusb` should show `2e8a:0003 Raspberry Pi RP2 Boot`.

Optional: reflash Katapult over USB (UF2) if needed.

Prebuilt Katapult UF2 (official):
- 1M CAN: `https://cdn.mellow.klipper.cn/BL/FLY_SHT36V3_SB2040V3_katapult_CAN_1M.uf2`
- 500K CAN: `https://cdn.mellow.klipper.cn/BL/FLY_SHT36V3_SB2040V3_katapult_CAN_500K.uf2`

USB flash command from Klipper tree (when board is in RP2 Boot mode):
```bash
cd ~/klipper
make flash FLASH_DEVICE=2e8a:0003
```

---

## Step 2 — Set up CAN network on Pi

```bash
sudo nano /etc/network/interfaces.d/can0
```

Contents:
```
allow-hotplug can0
iface can0 can static
  bitrate 1000000
  up ifconfig $IFACE txqueuelen 1024
```

```bash
sudo ip link set up can0 type can bitrate 1000000
sudo systemctl restart networking
```

Verify the interface is up:
```bash
ip -details link show can0
```

---

## Step 3 — Flash Klipper to SHT36

```bash
cd ~/klipper
make menuconfig
```

Settings:
```
Enable extra low-level options: Yes
Micro-controller Architecture:  Raspberry Pi RP2040
Bootloader offset:              16KiB bootloader
Communication interface:        CAN bus
CAN RX gpio number:             1
CAN TX gpio number:             0
CAN bus speed:                  1000000
GPIO pins at startup:           !gpio5
```

```bash
make

# Discover UUID of SHT36 on CAN:
python3 ~/klipper/lib/canboot/flash_can.py -q

# Flash Klipper:
python3 ~/klipper/lib/canboot/flash_can.py -u <UUID>
```

Alternative UUID query method:
```bash
~/klippy-env/bin/python ~/klipper/scripts/canbus_query.py can0
```

---

## Step 4 — Add SHT36 MCU to printer.cfg

Once Klipper sees the board, add to `printer.cfg`:

```ini
[mcu sht36]
canbus_uuid: <paste UUID from step 3>
# canbus_interface: can0  # only needed if interface is not can0
```

Restart Klipper and confirm `sht36` shows as connected in Mainsail before proceeding.

---

## Step 5 — Migrate components (safe order)

| Order | What to migrate | Notes |
|-------|----------------|-------|
| **1st** | Extruder motor + TMC2209 | Lowest risk, test cold first |
| **2nd** | Heater + PT1000 together | Must be migrated as a pair (thermal safety) |
| **3rd** | Hotend fan + part fan | Cold test each fan output |
| **4th** | Beacon probe (if re-routing through SHT36) | Re-calibrate offsets after |

For each step, change pin prefix from bare `PXX` to `sht36:PXX`.
Exact pin names: see [official pinout](https://mellow.klipper.cn/#/board/fly_sht36_v3_max/pinout).

### Example: extruder motor migration

Before (on Fly Super 8 M3 position):
```ini
[extruder]
step_pin: PE14
dir_pin: PE8
enable_pin: !PE9
...

[tmc2209 extruder]
uart_pin: PE7
```

After (on SHT36):
```ini
[extruder]
step_pin: sht36:<step_pin>    # from SHT36 pinout
dir_pin: sht36:<dir_pin>
enable_pin: !sht36:<en_pin>
...

[tmc2209 extruder]
uart_pin: sht36:<uart_pin>    # internal UART on SHT36
```

> Note: the Super 8 M3 position (PE14/PE8/PE9/PE7) is freed up after migration
> and can be disabled or repurposed.

---

## Step 6 — Post-migration calibration

After all components are migrated:

1. PID tune hotend:
   ```
   PID_CALIBRATE_EXTRUDER   # already in your macros
   ```
2. Extruder rotation distance calibration (Orbiter V2 baseline: `4.637`)
3. Re-run Beacon calibration:
   ```
   AUTO_BEACON_CALIBRATE    # already in your beacon.cfg macros
   ```
4. Re-run bed mesh
5. Re-tune pressure advance (current: `0.02`)

---

## Rollback

If anything goes wrong, restore from your backup config and revert `printer.cfg`
pin references back to the original Super 8 pin names. The Fly Super 8 M3 position
was the original extruder slot — all original pins are documented in `printer.cfg`.
