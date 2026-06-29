# 2026-06-29 - Fly Eddy median/MAD diagnostics sync

## Goal
Sync the updated Klipper eddy diagnostics to the vzbot Pi for live testing.

## Pre-change
- The local Klipper fork had been updated to use median-based live frequency sampling.
- Backlash reporting was changed to summarize with median and MAD instead of avg/std.
- The live Pi checkout still needed the refreshed `probe_eddy_current.py` copy.

## Post-change
- Live Pi Klipper checkout updated at `/home/lianxu/klipper/klippy/extras/probe_eddy_current.py`.
- Klipper restarted successfully and came back `active`.
- Live query validation succeeded:
  - `PROBE_EDDY_CURRENT_QUERY CHIP=fly_eddy`
  - Output now reports `freq_median=...` and calibrated height.

## Steps
1. Backed up the live Pi Klipper file with a timestamped `.bak` copy.
2. Synced the updated `probe_eddy_current.py` from the local Klipper fork to the Pi.
3. Restarted Klipper and confirmed the service was active.
4. Sent a live eddy query through the Klipper PTY to verify the new output path.

## Key commands
```bash
ssh lianxu@vzbot.local "cp /home/lianxu/klipper/klippy/extras/probe_eddy_current.py \
  /home/lianxu/klipper/klippy/extras/probe_eddy_current.py.bak.$(date +%Y%m%d-%H%M%S)"
rsync -a /Users/xulian/projects/klipper/klippy/extras/probe_eddy_current.py \
  lianxu@vzbot.local:/home/lianxu/klipper/klippy/extras/probe_eddy_current.py
ssh lianxu@vzbot.local "python3 -m py_compile /home/lianxu/klipper/klippy/extras/probe_eddy_current.py && sudo systemctl restart klipper && systemctl is-active klipper"
```

## Follow-ups
- Re-test `PROBE_EDDY_CURRENT_ESTIMATE_BACKLASH CHIP=fly_eddy` with the updated median/MAD summary.
- If the PR feedback changes again, keep the same live-stream wording and adjust only the summary text.