# 2026-06-29 - Eddy calibration macro split into 2 steps

## Goal
Fix the eddy calibration macro so it follows the required Klipper sequence after setting
`frequency: 40000000`.

## Pre-change
- `CALIBRATE_BEACON` only ran `LDC_CALIBRATE_DRIVE_CURRENT` and printed a follow-up hint.
- After changing LDC1612 reference frequency, old calibration mapping was invalid and produced
  out-of-range errors until re-calibration.
- No dedicated macro existed for the second calibration stage.

## Post-change
- `CALIBRATE_BEACON` is now explicitly step 1/2: drive current calibration only.
- Added `CALIBRATE_EDDY_HEIGHT` as step 2/2 to run `PROBE_EDDY_CURRENT_CALIBRATE CHIP=fly_eddy`.
- Updated both repo config and live Pi config (`/home/lianxu/printer_data/config/beacon.cfg`).
- Restarted Klipper and verified service state is `active`.
- After re-calibration on live Pi, `CHECK_Z` and `CHECK_BACKLASH` both returned `status=ok`.
- Live query now reports ~4.37 MHz (`freq_median=4371699.542Hz`) and valid height at ~3.0 mm.

## Steps
1. Updated `new_config/beacon.cfg` macro definitions to a two-stage workflow.
2. Backed up live `beacon.cfg` on the Pi with a timestamped `.bak` suffix.
3. Synced updated `beacon.cfg` to the live printer config path.
4. Restarted Klipper and verified the new macro blocks are present.
5. Synced live `printer_data/config/printer.cfg` back into repo `new_config/printer.cfg` after successful re-calibration.

## Key commands
```bash
ssh lianxu@vzbot.local "cp /home/lianxu/printer_data/config/beacon.cfg \
  /home/lianxu/printer_data/config/beacon.cfg.bak.$(date +%Y%m%d-%H%M%S)"
rsync -a /Users/xulian/projects/vzbot/new_config/beacon.cfg \
  lianxu@vzbot.local:/home/lianxu/printer_data/config/beacon.cfg
ssh lianxu@vzbot.local "sudo systemctl restart klipper && systemctl is-active klipper"
```

## Follow-ups
- Calibration flow completed and validated on live Pi (`CHECK_Z` + `CHECK_BACKLASH` both `status=ok`).
- Synced updated live `printer.cfg` calibration block (`#*# [probe_eddy_current fly_eddy] calibrate = ...`) into repo `new_config/printer.cfg`.
- Optional: decide whether to also mirror live fan tuning drift (`[fan] max_power/cycle_time`) into repo.

## Validation snapshot
- `CHECK_Z`:
  - `freq_median=4371699.542Hz height=2.996046mm ... status=ok`
- `CHECK_BACKLASH` summary:
  - `estimate_median=0.006902mm`
  - `estimate_mad=0.000174mm`
  - `estimate_min=0.005749mm`
  - `estimate_max=0.007076mm`
  - `status=ok`