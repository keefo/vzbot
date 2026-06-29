# 2026-06-29 - Safe Z Home z_hop tuned for CHECK_Z

## Goal
Allow `CHECK_Z` to work immediately after `G28` with the Fly Eddy probe by lowering post-home Z from an out-of-range height.

## Pre-change
- `[safe_z_home]` in `printer.cfg` used `z_hop: 5`.
- Fly Eddy calibrated range is about `0.050000..4.050000 mm`.
- Running `G28` then `CHECK_Z` could report:
  - `probe_eddy_current sensor not in valid range ... hint=move nozzle closer to bed (decrease Z)`

## Post-change
- `[safe_z_home] z_hop` changed from `5` to `3`.
- `G28` followed by `CHECK_Z` now returns in-range live readings (`status=ok`).
- Change applied both in repo (`new_config/printer.cfg`) and live Pi config (`~/printer_data/config/printer.cfg`).

## Steps
1. Updated repo config: `new_config/printer.cfg` -> `z_hop: 3`.
2. Backed up live config to timestamped file and applied same edit on Pi.
3. Restarted Klipper and verified service health.
4. Validated with direct command sequence: `G28` then `CHECK_Z`.

## Key commands
```bash
# On Pi: backup + edit + restart
cp ~/printer_data/config/printer.cfg ~/printer_data/config/printer.cfg.bak.<timestamp>
sed -i 's/^z_hop: 5$/z_hop: 3/' ~/printer_data/config/printer.cfg
sudo systemctl restart klipper

# Validation (via klippy serial)
G28
CHECK_Z
```

## Follow-ups
- If any homing edge cases appear (clips/parts near bed), increase cautiously to `z_hop: 3.5`.
- Keep `CHECK_Z` as a quick post-home sanity check when changing probe calibration.
