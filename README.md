# vzbot 330
myvzbot

## System Information
- **Motherboard**: Fly Super 8 V1.3
  - [Pinout Diagram](doc/fly-super8_pins.svg)
  - [Reference Documentation](doc/Fly-Super8%20.pdf)
- **Kit**: Mellow Kit
- **Raspberry Pi**: 
  - **Model**: Raspberry Pi 5 Model B Rev 1.0
  - **Serial**: 9034753a960b8f5f
  - **Memory**: 4GB
  - **SD Card**: SanDisk SR64G, 59.5 GiB
  - **OS**: Debian GNU/Linux 12 (bookworm)
  - **Kernel**: 6.12.93+rpt-rpi-2712

# Hardware & Upgrades

## Toolhead
- **Mellow Fly SHT36 V3 Max** - Acquired for toolhead upgrade

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
