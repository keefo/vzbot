# 2026-06-29 - Fly Eddy CHECK_BACKLASH implementation

## Goal
Replace legacy Beacon-only backlash command with an Eddy-native backlash estimator that works with the current SHT36 + fly_eddy setup.

## Pre-change
- `CHECK_BACKLASH` macro still called `BEACON_ESTIMATE_BACKLASH`.
- Beacon is no longer active on this printer, so the old command path was stale.
- Existing custom eddy helper already provided `PROBE_EDDY_CURRENT_QUERY` only.

## Post-change
- New Klipper command implemented in `probe_eddy_current.py`:
  - `PROBE_EDDY_CURRENT_ESTIMATE_BACKLASH CHIP=fly_eddy`
- `CHECK_BACKLASH` macro now calls this command.
- Live validation succeeded after `G28`:
  - `probe_eddy_current fly_eddy backlash: ... estimate=0.006440mm ... status=ok`

## Steps
1. Updated macro wiring in `new_config/beacon.cfg`:
   - `CHECK_BACKLASH` now runs `PROBE_EDDY_CURRENT_ESTIMATE_BACKLASH CHIP=fly_eddy`.
2. Extended live Klipper helper class (`EddyQueryHelper`) to add backlash command:
   - Added command registration for `PROBE_EDDY_CURRENT_ESTIMATE_BACKLASH`.
   - Refactored query sampling into shared `_collect_height(...)`.
   - Implemented two-direction approach test at the same Z target and reports absolute delta as backlash estimate.
3. Restarted Klipper and verified command output through the Klipper serial console.

## Key commands
```bash
# Run after homing
G28
CHECK_BACKLASH

# Direct command variant with optional tuning
PROBE_EDDY_CURRENT_ESTIMATE_BACKLASH CHIP=fly_eddy TRAVEL=0.5 SPEED=10 SAMPLES=40
```

## Follow-ups
- Try a few repeated runs and average the estimate for a more stable backlash number.
- If needed, tune defaults (`TRAVEL`, `SPEED`) for your mechanics and keep values in a macro wrapper.
- Keep patch artifacts for post-update reapply:
  - `doc/klipper_patches/probe_eddy_current_query.patch`
  - `doc/klipper_patches/probe_eddy_current_backlash.patch`

## Update (Runtime tuning)
- Multi-cycle behavior was tuned to feel closer to Beacon while avoiding long blocking runs.
- New command defaults:
  - `CYCLES=5` (was 8)
  - `SAMPLES=20` (lower sampling load)
- Added per-cycle progress output so the console shows active progress during measurement.
- Macro default now uses:
  - `PROBE_EDDY_CURRENT_ESTIMATE_BACKLASH CHIP=fly_eddy CYCLES=5 SAMPLES=20`

## Update (Beacon-like reporting)
- Per-cycle output now includes both frequency and converted height on each side of the approach:
  - `above=<freq>/<height> below=<freq>/<height> estimate=<delta>`
- End-of-run output now includes:
  - Full per-cycle estimate list (`estimates_mm=[...]`)
  - Aggregated stats (`avg`, `median`, `min`, `max`, `std`)
