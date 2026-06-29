# SHT36 V3 Max toolhead — CAN migration

**Goal:** Bring the Mellow Fly SHT36 V3 Max online as a CAN toolhead MCU and migrate the
toolhead components onto it, one safe step at a time. This log is updated as each step
completes.

## Pre-change
- Main board (Super 8 Pro H723) running Klipper in USB-to-CAN bridge mode; `can0` up at 1 Mbit.
- SHT36 V3 Max (RP2040) present on the CAN bus but **still in Katapult** (`85a1452bd027`).
- All toolhead components (extruder, hotend heater, thermistor, fans, accel) still wired to
  the main board.

## Post-change
- **Step 1 done (2026-06-28):** SHT36 now runs Klipper over CAN (`85a1452bd027` →
  `Application: Klipper`).
- **Step 2 done (2026-06-28):** `[mcu sht36]` added to `printer.cfg`; Klipper restarted and
  `Configured MCU 'sht36' (1024 moves)` — toolhead MCU connects cleanly. No pins moved yet;
  printer still fully functional on the main board. Mirrored to `new_config/printer.cfg`.
- **Step 3 done (2026-06-28):** Hotend temperature sensor moved to the SHT36. The onboard
  MAX31865 (PT100/PT1000) was found **hardware-faulty** (sense/RTDIN path open) and abandoned.
  Using the SHT36 **native thermistor input** instead: `sensor_pin: sht36:gpio27`,
  `sensor_type: PT1000`, PT1000 pullup jumper installed (1k). Reads ~17 °C low at
  `pullup_resistor: 1000`; trimmed to **1063** so the hotend matches the bed/chamber ambient
  (~25 °C). Heater is **still on the main board PB0** — sensor-only move for now. Mirrored to
  `new_config/printer.cfg`.
- **Step 4 done (2026-06-28):** X endstop moved to the SHT36 ENDSTOP header on **gpio16**:
  `[stepper_x] endstop_pin: ^sht36:gpio16` (was `PG9`). `^` = internal pullup for a 2-wire
  switch to GND. `QUERY_ENDSTOPS` reads `open` at rest and **TRIGGERED when pressed (verified
  by hand)**. Mirrored to `new_config/printer.cfg`.
- **Step 5 done (2026-06-28):** Extruder motor + driver moved to the SHT36 **E-MOT** (onboard
  TMC2209): `[extruder]` `step_pin: sht36:gpio7`, `dir_pin: sht36:gpio6`,
  `enable_pin: !sht36:gpio14`; `[tmc2209 extruder] uart_pin: sht36:gpio15`. `run_current` 0.85
  and `sense_resistor` 0.110 unchanged (same driver spec). Restarted, Ready, no TMC UART
  errors. Cold motion test: **direction correct** (verified by hand), motor holds. Mirrored to
  `new_config/printer.cfg`.
- **Step 6 done (2026-06-28):** Beacon probe removed; **eddy current probe (Mellow LDC1612)**
  added on the SHT36 over I²C. `[probe_eddy_current fly_eddy]` `sensor_type: ldc1612`,
  `i2c_mcu: sht36`, `i2c_bus: i2c1f` (gpio22/gpio23 hardware I²C — confirmed valid from the
  MCU bus map). `[stepper_x]`/Z homing keeps `probe:z_virtual_endstop`, now provided by the
  eddy. The dead `[beacon]` serial section and `[resonance_tester] accel_chip: beacon` are
  commented out in `beacon.cfg`, and the `#*# [beacon model default]` autosave block was
  removed from `printer.cfg` (Klipper parses autosave, so it was forcing a `[beacon]` section
  and halting boot). `[bed_mesh]` kept (probe-agnostic). Restarted → **Ready, no I²C/LDC
  errors**, firmware reports `CONFIG_WANT_LDC1612=y`. **Not yet calibrated — no Z homing until
  calibration is done.** Input shaping is unavailable until the accelerometer is moved to the
  SHT36 LIS2DW. Mirrored to `new_config/`.
- **Step 6b correction (2026-06-28):** The eddy I²C was first set to `i2c1f` (guess) which
  reached “ready” but never actually read the LDC (Klipper defers the I²C read until probing).
  The board diagram (`doc/sht36_v3_max/pin.webp`) shows the LDC1612 is on **`i2c1e`** at
  **address `43`**. Corrected to `i2c_bus: i2c1e` + `i2c_address: 43`; the eddy now reports a
  live `freq=~50 MHz` — confirmed communicating. (This also freed gpio23 for the heater.)
- **Step 7 done (2026-06-28):** Hotend heater moved to the SHT36 **HEAT0 = gpio23**:
  `[extruder] heater_pin: PB0` → `sht36:gpio23`. Restarted → Ready, no pin conflict,
  `extruder pwm=0`. Heater + PT1000 are now both on the toolboard. **PID not re-tuned yet and
  no heating performed** — run `PID_CALIBRATE EXTRUDER` before printing (the gpio23 MOSFET is a
  different output than the old PB0). Mirrored to `new_config/printer.cfg`.

## Steps
1. **Flash Klipper onto the SHT36 (DONE 2026-06-28)**
   - Backed up the bridge `~/klipper/.config` first (a SHT36 build overwrites it):
     Pi `.config.bridge.bak.20260628-000943`; repo `doc/firmware_backup/super8pro_h723/`.
   - Built RP2040/CAN firmware non-interactively (seed `.config` + `make olddefconfig` + `make`):
     arch `MACH_RPXXXX` + `MACH_RP2040`, 16KiB bootloader (`RPXXXX_FLASH_START_4000`,
     app @ `0x10004000`), CAN bus RX=gpio1 / TX=gpio0, 1 Mbit, startup pin `!gpio5`.
   - Flashed over CAN via Katapult to `85a1452bd027`; verified. Artifacts saved to
     `doc/firmware_backup/sht36_v3_max/` (`klipper_sht36_can.bin` SHA `c00a591e…` + `.config`).
2. **Add `[mcu sht36]` and verify (DONE 2026-06-28)**
   - Backed up live `printer.cfg` (`printer.cfg.bak.20260628-001430`), inserted `[mcu sht36]`
     with `canbus_uuid: 85a1452bd027` after the main `[mcu]` block.
   - Restarted Klipper; log shows `Loaded MCU 'sht36'` + `Configured MCU 'sht36' (1024 moves)`,
     service active, no errors. Mirrored to `new_config/printer.cfg`.
3. **Hotend thermistor → SHT36 (DONE 2026-06-28)**
   - Diagnosed the onboard MAX31865 as defective (value rails to open/65535, fault 129;
     FORCE side OK but RTDIN dead — not a config/DIP/wiring issue). Abandoned it.
   - Switched `[extruder]` to the SHT36 native thermistor input: `sensor_type: PT1000`,
     `sensor_pin: sht36:gpio27`. Installed the gpio27 PT1000 pullup jumper (1k / `CONN`).
   - Calibrated: Klipper has no sensor offset field — trimmed `pullup_resistor` (1000 → 1063)
     using bed/chamber (~25 °C) as the ambient reference (IR gun reads low on shiny metal).
     Hotend then read 25.05 °C vs chamber 25.14 °C. Heater left on main board PB0.
4. **X endstop → SHT36 (DONE 2026-06-28)**
   - Wired the X microswitch to the SHT36 ENDSTOP header (signal = gpio16, + GND).
   - `[stepper_x] endstop_pin: PG9` → `^sht36:gpio16`. Restarted, `QUERY_ENDSTOPS` = `open`
     at rest, `TRIGGERED` when pressed (hand-tested). Safe to home X.
5. **Extruder motor + TMC2209 → SHT36 E-MOT (DONE 2026-06-28)**
   - SHT36 onboard driver pins (from board pinout): STEP gpio7, DIR gpio6, EN gpio14,
     UART gpio15.
   - `[extruder]` step/dir/enable → `sht36:gpio7` / `sht36:gpio6` / `!sht36:gpio14`;
     `[tmc2209 extruder] uart_pin: PE7` → `sht36:gpio15`. Kept run_current 0.85 / sense 0.110.
   - Restarted (Ready, no TMC errors). Cold `G1 E10 F60` test: gear turns the correct feed
     direction, motor energized. No `!` flip needed on dir_pin.
6. **Beacon → SHT36 eddy probe (LDC1612) (DONE 2026-06-28)**
   - Beacon was serving three roles: Z probe (`probe:z_virtual_endstop`), `[bed_mesh]`
     provider, and accelerometer (`[resonance_tester] accel_chip: beacon`).
   - Added `[probe_eddy_current fly_eddy]`: `sensor_type: ldc1612`, `i2c_mcu: sht36`,
     `i2c_bus: i2c1f`, `x_offset/y_offset: 0` (TBD), `z_offset: 1.0` (placeholder).
   - Commented out `[beacon]` + `[resonance_tester]` in `beacon.cfg`; **removed** the
     `#*# [beacon model default]` autosave block from `printer.cfg` (Klipper strips the
     `#*#` prefix and parses it, which re-creates a `[beacon]` section → boot halt).
   - Restarted → Ready, no I²C/LDC errors; `i2c1f` = gpio22/gpio23 confirmed from the MCU
     bus map. `[bed_mesh]` retained.
   - **Calibration still required** before any Z home (see Follow-ups). Input shaping is off
     until the accelerometer moves to the SHT36 LIS2DW.
   - NOTE: i2c bus corrected `i2c1f` → **`i2c1e` + `i2c_address: 43`** (per board diagram);
     eddy now reports a live frequency. This also freed gpio23 for the heater.
7. **Hotend heater → SHT36 HEAT0 (gpio23) (DONE 2026-06-28)**
   - `[extruder] heater_pin: PB0` → `sht36:gpio23` (HEAT0 per `pin.webp`). Restarted, Ready,
     no pin conflict, `extruder pwm=0`. Heater + PT1000 now both on the toolboard.
   - **No heating done yet; PID not re-tuned.** Run `PID_CALIBRATE EXTRUDER TARGET=<temp>` +
     `SAVE_CONFIG` before printing, and validate the PT1000 reading at temperature.
8. **Eddy probe calibrated (DONE 2026-06-28)**
   - `LDC_CALIBRATE_DRIVE_CURRENT CHIP=fly_eddy` → `reg_drive_current = 14`; `SAVE_CONFIG`.
   - Height map: `SET_KINEMATIC_POSITION Z=10`, parked center, `PROBE_EDDY_CURRENT_CALIBRATE
     CHIP=fly_eddy`, lowered to paper-grip (Z0), `ACCEPT`. Noise ~0.001 mm, range 30.7 kHz,
     table 0.05–4.05 mm. `SAVE_CONFIG`.
9. **Homing fixed (DONE 2026-06-28)** — first `G28` crashed Z (no safe-z, 30 mm/s too fast,
   eddy only senses ~4 mm). Added `[safe_z_home] home_xy_position: 150,142 z_hop:5`;
   `[stepper_z] homing_speed 30→8`, `second_homing_speed 5→3`.
10. **Bed mesh → eddy continuous scan (DONE 2026-06-28)** — `CALIBRATE_BED_MESH` now
    `BED_MESH_CALIBRATE METHOD=rapid_scan`; added `[bed_mesh] scan_overshoot: 8`. Back-edge
    cliff fixed by `mesh_max 280→270` (sensor was over rear frame). `CALIBRATE_BEACON`
    repurposed to run the eddy drive-current cal.
11. **Accelerometer → SHT36 LIS2DW (DONE 2026-06-28)** — `[lis2dw]` CS gpio12 / MOSI gpio3 /
    MISO gpio4 / SCK gpio2; `[resonance_tester] accel_chip: lis2dw, probe_points: 150,142,20`.
    `ACCELEROMETER_QUERY` dev_id 44, gravity reads. `SHAPER_CALIBRATE` repeatable: X mzv
    ~75.6 Hz, Y mzv ~47 Hz (0% vibration). Input shaping restored; Beacon fully removed.

## Key commands
```bash
# Back up bridge config before an SHT36 build clobbers ~/klipper/.config
cp ~/klipper/.config ~/klipper/.config.bridge.bak.$(date +%Y%m%d-%H%M%S)

# Seed RP2040/CAN config, resolve, build
# (CONFIG_MACH_RPXXXX=y, CONFIG_MACH_RP2040=y, CONFIG_RPXXXX_FLASH_START_4000=y,
#  CONFIG_RPXXXX_CANBUS=y, RX=1, TX=0, CONFIG_CANBUS_FREQUENCY=1000000,
#  CONFIG_INITIAL_PINS="!gpio5")
make olddefconfig && make

# Flash over CAN (SHT36 in Katapult)
python3 ~/katapult/scripts/flashtool.py -i can0 -u 85a1452bd027 -f out/klipper.bin

# Confirm it now runs Klipper
python3 ~/katapult/scripts/flashtool.py -i can0 -q
```

## Follow-ups
- After SHT36 build, `~/klipper/.config` holds the SHT36 config — restore the bridge `.config`
  before any future main-board rebuild.
- Mirror every change into `new_config/printer.cfg` (done through Step 4).
- Eddy probe calibrated; set real `x_offset`/`y_offset` (eddy coil vs nozzle) and `z_offset`
  once the physical offset is measured (currently 0/0/1.0).
- Y resonance ~47 Hz is low → keep `max_accel` ≤ ~6000; check Y belt tension / mass.
- **Validate the PT1000 at temperature** during the heater bring-up — the 1063 pullup is a
  single-point room-temp cal and may need a small re-trim at print temp.
- The faulty MAX31865 block is left commented in `printer.cfg` (documents the abandoned path);
  consider RMA if PT100 is ever wanted.
- Re-run hotend PID, pressure advance, and input shaper after the heater/accel move.
