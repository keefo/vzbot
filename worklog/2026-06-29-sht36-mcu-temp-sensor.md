## Goal

Add a dedicated SHT36 toolhead MCU temperature sensor to Klipper config for
monitoring in UI and macros.

## Pre-change

- `new_config/printer.cfg` did not have a SHT36 MCU temperature sensor section.
- Live Pi config `~/printer_data/config/printer.cfg` also did not have this
  section.

## Post-change

- Added `[temperature_sensor sht36_mcu]` with:
  - `sensor_type: temperature_mcu`
  - `sensor_mcu: sht36`
  - `min_temp: 0`
  - `max_temp: 120`
- Applied in both repo config (`new_config/printer.cfg`) and live Pi config.
- Restarted Klipper and verified service is active.

## Steps

1. Added sensor section to `new_config/printer.cfg`.
2. Verified local config parse showed no errors.
3. Backed up live Pi config to timestamped `.bak`.
4. Inserted same sensor section into live Pi `printer.cfg`.
5. Restarted Klipper service and verified status `active`.
6. Confirmed section exists in live Pi config.

## Key commands

```bash
# local repo check
git diff -- new_config/printer.cfg

# live Pi update (via local alias)
vzbot
cp ~/printer_data/config/printer.cfg \
  ~/printer_data/config/printer.cfg.bak.$(date +%Y%m%d-%H%M%S)

# restart + verify
sudo systemctl restart klipper
systemctl is-active klipper
```

## Follow-ups

- In Mainsail/Fluidd, confirm `sht36_mcu` appears in temperature widgets.
- If desired, add `gcode_id` for concise display label.
