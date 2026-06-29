# 2026-06-29 - Fly Eddy live distance query (Option A)

## Goal
Add and validate a local Klipper host patch that exposes a manual Fly Eddy live query command for diagnostics.

## Pre-change
- Fly Eddy was connected and configured through `probe_eddy_current` on SHT36.
- Stock Klipper did not expose a direct one-shot G-code command to print current calibrated eddy distance in this setup.
- A local patch had already been prepared and applied on the Pi to `~/klipper/klippy/extras/probe_eddy_current.py`.
- Moonraker HTTP endpoint on localhost required authentication from this shell context (`401 Unauthorized`), so unauthenticated HTTP was not a reliable validation path.

## Post-change
- Patched command is active and executable:
  - `PROBE_EDDY_CURRENT_QUERY CHIP=fly_eddy`
- Runtime validation confirmed command registration and execution through Klipper PTY (`~/printer_data/comms/klippy.serial`).
- Current result at test position: `probe_eddy_current sensor not in valid range` (expected when the sensor is outside calibrated Z/frequency envelope).
- No Klipper crash; printer remained in `Ready` state and command returned `ok` after processing.

## Steps
1. Attempted command invocation through Moonraker HTTP API on localhost; request was blocked by auth (`401 Unauthorized`).
2. Switched to direct Klipper PTY path for deterministic command/response capture.
3. Sent `PROBE_EDDY_CURRENT_QUERY CHIP=fly_eddy` to `~/printer_data/comms/klippy.serial` while capturing `/dev/pts/0` output.
4. Correlated PTY response with `klippy.log` entries to confirm the command path and runtime behavior.

## Key commands
```bash
# Capture direct Klipper PTY response while sending the query command
PTY=$(readlink -f ~/printer_data/comms/klippy.serial)
(timeout 4s stdbuf -o0 cat "$PTY" > /tmp/klippy_pty_capture.txt || true) &
sleep 0.3
printf "PROBE_EDDY_CURRENT_QUERY CHIP=fly_eddy\n" > ~/printer_data/comms/klippy.serial

# Inspect response and logs
sed -n '1,200p' /tmp/klippy_pty_capture.txt
tail -n 120 ~/printer_data/logs/klippy.log | grep -nE 'probe_eddy_current|PROBE_EDDY_CURRENT_QUERY|sensor not in valid range|freq=.*height='
```

## Follow-ups
- Re-test with nozzle/sensor in a known calibrated range to observe the positive path output with frequency and computed height.
- Optional convenience macro (if desired): add `CHECK_EDDY_Z` that calls `PROBE_EDDY_CURRENT_QUERY CHIP=fly_eddy`.
- Keep patch artifact in repo (`doc/klipper_patches/probe_eddy_current_query.patch`) and re-apply after Klipper updates.

## Update (Range Hint)
- The command handler was improved to include calibration context when out of range:
  - Message now includes measured `freq`, computed `height`, calibrated window `min..max`, and directional hint (`decrease Z` or `increase Z`).
- Live module on Pi was restored from a known-good backup, then updated with the new range-hint branch and restarted successfully.
- Current command test on this host position returned in-range `status=ok`, so no error hint was emitted in that final validation sample.
