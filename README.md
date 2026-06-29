# vzbot 330
myvzbot

## System Information
- **Motherboard**: Fly Super 8 V1.3 (controller MCU: **STM32H723**, i.e. Super 8 "Pro" H723 silicon)
  - [Pinout Diagram](doc/fly-super8_pins.svg)
  - [Reference Documentation](doc/Fly-Super8%20.pdf)
  - Flashed over USB **DFU** (no SD-card bootloader); runs Klipper in USB-to-CAN bridge mode (see [Firmware & CAN Bus](#firmware--can-bus))
- **Kit**: Mellow Kit
- **Raspberry Pi**: 
  - **Model**: Raspberry Pi 5 Model B Rev 1.0
  - **Serial**: 9034753a960b8f5f
  - **Memory**: 4GB
  - **SD Card**: SanDisk SR64G, 59.5 GiB
  - **OS**: Debian GNU/Linux 12 (bookworm)
  - **Kernel**: 6.12.93+rpt-rpi-2712

## SSH Access

Use the local shortcut command:

```bash
vzbot
```

> **Note:** `vzbot` is a personal SSH alias defined in my local shell profile
> (not committed to this repo). Define your own alias pointing to your printer host.

# Hardware & Upgrades

## Toolhead
- **Mellow Fly SHT36 V3 Max** - Acquired for toolhead upgrade
  - [Integration Guide](doc/sht36_v3_max/integration_guide.md)
  - [Official Intro](https://mellow.klipper.cn/#/board/fly_sht36_v3_max/intro)
  - [Official Pinout](https://mellow.klipper.cn/#/board/fly_sht36_v3_max/pinout)
  - **CAN UUID**: `85a1452bd027`
  - **Status**: Running Klipper over CAN (firmware flashed 2026-06-28); toolhead pin migration pending

## Firmware & CAN Bus
The Super 8 Pro (H723) runs Klipper in **USB-to-CAN bridge mode**. The Pi connects to
the board over the USB-C cable, but all Klipper communication is now CAN protocol
tunneled over that cable. The board also bridges onto the physical CAN wires
(PB8/PB9, CANH/CANL) that reach the SHT36 toolhead.

> **Last upgraded:** 2026-06-27 (see [Worklog](#worklog)).

- **Main MCU (Super 8 Pro H723)**
  - **CAN UUID**: `538e6d5fb457`
  - **USB identity (bridge)**: `1d50:606f` (Geschwister Schneider / `gs_usb`)
  - **App layout**: Katapult bootloader at `0x08000000`, Klipper app at `0x08020000`
  - **CAN bitrate**: `1000000` (1 Mbit)
- **Flashing**: USB **DFU** + Katapult (the H723 has **no SD-card bootloader**). Full
  command sequence and rollback artifacts are in the
  [worklog](#worklog) and [firmware backup](doc/firmware_backup/super8pro_h723/).
- **can0 interface**: brought up automatically by a systemd service at boot
  (`/etc/systemd/system/can0.service`, hotplug-tied) at 1 Mbit with `txqueuelen 128`.
- **List CAN devices**: `python3 ~/katapult/scripts/flashtool.py -i can0 -q`

## Worklog
Detailed upgrade logs live in [`worklog/`](worklog/), one file per change (named by date):
- [2026-06-28 — SHT36 V3 Max toolhead: CAN migration](worklog/2026-06-28-sht36-toolhead-migration.md)
- [2026-06-27 — Super 8 Pro: USB serial → USB-to-CAN bridge](worklog/2026-06-27-super8-usb-to-can-bridge.md)

## Components
- **Z Axis Lead Screw**: T8, 1mm Pitch, 500mm Length
  - **Bearings**: 4x Bearing 608
  - **Smooth Rods**: 4x 10mm Linear Shaft, 500mm
  - **Linear Bearings**: 4x LM10LUU (10mm)
  - **Oldham Couplers**: 1mm pitch
  - **Leadscrew Pulley**: 2x 40T 2GT, Z axis 2:1 ratio, 6mm width
  - **Z Motor Pulley**: GT2 20T, 5mm ID
- **Z Belt**: GT2 Closed Belt, 1100mm Length, 6mm Width
- **Z Motor**: LDO 60mm 1.8
- **XY Motors (AWD)**: 2x X motors + 2x Y motors (LDO Super Motor 42STH48 2804AC-R)
- **XY Belts**: GT3 Open Belt 6mm 5m
- **Z Motor Stepper Driver**: TMC2209
- **XY Motors Stepper Drivers (AWD)**: 4x TMC5160HV Pro 1.2
- **Power Supplies**:
  - Mean Well LRS-350-24 DC
  - Mean Well LRS-350-48 DC
- **Extruder**: Orbiter V2
  - Nozzle: 0.4mm
  - Filament Diameter: 1.75mm
  - Thermistor: PT1000
  - Max Extrude Temperature: 360°C
  - [Firmware Configuration Reference](doc/Orbiterv20FirmwareConfiguration-031c.pdf)
- **Bed Leveling Probe**: Beacon RevH
  - Proximity & Contact Sensor
  - X Offset: 0mm, Y Offset: 25mm
  - Mesh Grid: 80x80
  - [Beacon Documentation](https://docs.beacon3d.com/quickstart/)

## Part Cooling
- **Fan**: CPAP 7040
- **Relay**: SSR Solid State Relais DC / AC, 230V AC 10 A

## Board & Motor Positions
Based on Fly Super 8 V1.3 with Mellow Kit:
- **M1**: stepper_z (Z motor)
- **M2**: stepper_x (X motor)
- **M4**: stepper_x1 (X1 motor)
- **M5**: stepper_y (Y motor)
- **M6**: stepper_y1 (Y1 motor)

## Known Issues
- **M0 position: BROKEN** - Originally used for Z motor, now using M1 position instead
- **M7 motor position**: Has SPI communication issues (see [VzBot documentation](https://docs.vzbot.org/vz330_mellow/electronics/super_mellow))
- **IO2 endstop (PG11): BROKEN** - Using alternative endstop pin for stepper_x

# led

This LED code support btf-lighting LED strip. To be specific, it supports WS2814 DC24V Led Strip Light 4 in 1, 5M 420LEDS, Black PCB, RGB WW IP67.

https://vi.aliexpress.com/item/1005004794429155.html?spm=a2g0o.order_list.order_list_main.212.525f18021J0lzq&gatewayAdapt=glo2vnm


<img src="doc/led.jpg" />

```bash
cd ~/
git clone https://github.com/keefo/vzbot.git
./vzbot/led/setup.sh
```

# Configuration

> **Note:** `[mcu]` connects to the main board over CAN via `canbus_uuid: 538e6d5fb457`
> (USB-to-CAN bridge), not a serial port. Moonraker's update manager includes a
> `katapult` entry for bootloader updates.

Configuration files located in `new_config/` directory:
- `printer.cfg` - Main printer configuration
- `beacon.cfg` - Bed leveling sensor configuration
- `macro.cfg` - Macro definitions
- `shell_command.cfg` - Shell commands configuration
- `sound.cfg` - Sound configuration
- `moonraker.conf` - Moonraker server configuration
- `KAMP_Settings.cfg` - KAMP (Klipper Adaptive Meshing & Purging) settings
- `exclude_object.cfg` - Exclude object configuration
- `led.cfg` - LED configuration

# kill switch

Connect any simple maniacal key switch to PI gpio17 and ground.

```bash
cd ~/
git clone https://github.com/keefo/vzbot.git
./vzbot/kill_switch/setup.sh
```
