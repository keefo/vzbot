# Fly Eddy live Z-distance query plan

## Goal
Add a Beacon-like diagnostic command for the current Fly Eddy / LDC1612 probe so the printer can
report the live calibrated sensor-to-bed distance near the current toolhead position.

Target user experience:

```gcode
FLY_EDDY_QUERY CHIP=fly_eddy
```

Example response:

```text
fly_eddy: freq=50123456.789Hz height=1.238mm samples=40 range=0.050..4.050mm
```

This is intended as a diagnostic/readout tool, not as a replacement for homing, bed mesh, or
proper Z calibration.

## Current state
- Beacon was removed and replaced by `[probe_eddy_current fly_eddy]` using an LDC1612 over the
  SHT36 toolboard.
- Old Beacon commands/macros such as `BEACON_QUERY` and `CHECK_Z` no longer work because the
  `[beacon]` module is disabled.
- Klipper already has the important pieces for Fly Eddy:
  - `~/klipper/klippy/extras/ldc1612.py` reads raw LDC1612 frequency samples.
  - `~/klipper/klippy/extras/probe_eddy_current.py` maps frequency to calibrated height.
  - `EddyCalibration.freq_to_height(freq)` already converts frequency to height using the saved
    `calibrate = ...` table.
  - `LDC1612.add_client(cb)` can subscribe to measurement batches.
- The live config has saved calibration data for `[probe_eddy_current fly_eddy]`, so a query
  command can use the existing calibration table.

## Key distinction from Beacon
Beacon exposes a polished product-specific command set. Fly Eddy in Klipper exposes the probing
workflow, but not a convenient live distance query command. The missing feature is mostly a
Klipper host-side command, not new SHT36 MCU firmware.

The SHT36 MCU already reports LDC1612 measurements. The Pi-side Klipper Python code owns the
calibration model and is the right place to add a user-facing command.

## Solution options

### Option A: Local Klipper host patch
Patch `~/klipper/klippy/extras/probe_eddy_current.py` to register a new mux command for each
`[probe_eddy_current <name>]` section.

Possible command names:

```gcode
PROBE_EDDY_CURRENT_QUERY CHIP=fly_eddy
```

or shorter local-only naming:

```gcode
FLY_EDDY_QUERY CHIP=fly_eddy
```

Recommended name: `PROBE_EDDY_CURRENT_QUERY`, because it matches Klipper's existing
`PROBE_EDDY_CURRENT_CALIBRATE` naming style.

Pros:
- Uses existing Klipper internals directly.
- Can report calibrated height, average frequency, sample count, and validity range.
- Can later be shaped into an upstreamable patch.

Cons:
- Local patch may be overwritten by Klipper updates.
- Needs careful testing so the command does not leave LDC sampling clients active.

### Option B: External helper script
Write a separate Python script that connects to Klipper/Moonraker or reads bulk sensor data and
performs height conversion independently.

Pros:
- Does not modify Klipper source.
- Easier to experiment with quickly.

Cons:
- More fragile and likely duplicates Klipper calibration logic.
- Harder to access internal calibration/drift-compensation state correctly.
- Worse long-term maintenance.

### Option C: Upstream-style Klipper feature
Implement a clean `PROBE_EDDY_CURRENT_QUERY` command and prepare it as a minimal patch suitable
for submitting upstream.

Pros:
- Best long-term solution.
- Could help other Fly Eddy / LDC1612 users.

Cons:
- Requires stricter code style, broader testing, and likely discussion with Klipper maintainers.
- Upstream may prefer a different command shape or status API.

## Recommended approach
Start with Option A as a small local Klipper host patch. Keep the patch minimal and document it.
If it proves useful and stable, convert it into Option C later.

## Proposed command behavior

Command:

```gcode
PROBE_EDDY_CURRENT_QUERY CHIP=fly_eddy [SAMPLES=40] [SAMPLE_TIME=0.100]
```

Parameters:
- `CHIP`: probe section suffix, same style as `PROBE_EDDY_CURRENT_CALIBRATE CHIP=fly_eddy`.
- `SAMPLES`: optional number of samples to average. Default around 40.
- `SAMPLE_TIME`: optional collection window in seconds. Default around 0.100 seconds.

Response fields:
- `freq`: averaged raw LDC1612 frequency in Hz.
- `height`: calibrated sensor-to-bed height in mm.
- `samples`: number of sensor samples used.
- `min_height` / `max_height`: calibration table range.
- `status`: `ok`, `out_of_range`, or `not_calibrated`.

Possible response:

```text
fly_eddy: freq=50312345.123Hz height=1.237mm samples=39 range=0.050..4.050mm status=ok
```

## Implementation sketch

1. Back up the live Klipper module on the Pi:

   ```bash
   cp ~/klipper/klippy/extras/probe_eddy_current.py \
      ~/klipper/klippy/extras/probe_eddy_current.py.bak.$(date +%Y%m%d-%H%M%S)
   ```

2. Add a small query helper class to `probe_eddy_current.py`.

   The helper should:
   - Register a mux command with `gcode.register_mux_command(...)`.
   - Subscribe to `sensor_helper.add_client(...)` for a short sample window.
   - Average the collected frequency values.
   - Convert average frequency using `calibration.freq_to_height(freq_avg)`.
   - Reject heights that map to Klipper's `OUT_OF_RANGE` sentinel.
   - Always unsubscribe/stop cleanly after the command.

3. Register the helper inside `PrinterEddyProbe.__init__` after `self.sensor_helper` is created.

   Conceptual location:

   ```python
   self.sensor_helper = sensors[sensor_type](config, self.calibration)
   EddyQueryHelper(config, self.sensor_helper, self.calibration)
   ```

4. Restart Klipper:

   ```bash
   sudo systemctl restart klipper
   ```

5. Verify Klipper starts cleanly:

   ```bash
   tail -n 100 ~/printer_data/logs/klippy.log
   ```

6. Test near the bed, over metal and within the calibrated range:

   ```gcode
   PROBE_EDDY_CURRENT_QUERY CHIP=fly_eddy
   ```

7. Test expected error cases:
   - Probe too high above bed.
   - Probe over rear frame/edge.
   - Probe before calibration data is present.

8. Add a convenience macro only after the raw command works:

   ```ini
   [gcode_macro CHECK_EDDY_Z]
   gcode:
     PROBE_EDDY_CURRENT_QUERY CHIP=fly_eddy
   ```

## Validation plan

Minimum checks:
- Klipper service starts and remains active.
- `PROBE_EDDY_CURRENT_QUERY CHIP=fly_eddy` returns a frequency and height.
- Repeated reads at the same Z are stable within a small tolerance.
- Raising Z produces increasing/decreasing height in the expected direction.
- Querying outside the calibrated range gives a clear error instead of a misleading number.
- Existing `G28`, `PROBE_ACCURACY`, and `BED_MESH_CALIBRATE METHOD=rapid_scan` still work.

Recommended quick test sequence:

```gcode
G28 X Y
SET_KINEMATIC_POSITION Z=10
G0 X150 Y142 Z3 F6000
PROBE_EDDY_CURRENT_QUERY CHIP=fly_eddy
G0 Z2
PROBE_EDDY_CURRENT_QUERY CHIP=fly_eddy
G0 Z1
PROBE_EDDY_CURRENT_QUERY CHIP=fly_eddy
```

Expected behavior: reported height should change consistently as Z changes.

## Risks and limitations
- The reported distance is eddy coil to metal bed distance, not directly nozzle-to-bed distance.
- It is meaningful only over suitable metal target areas and within the calibration range.
- Temperature drift may affect readings. If `[temperature_probe]` drift compensation is later
  enabled, the query command should use the same compensated calibration path.
- A Klipper update may overwrite the local patch.
- A badly written client callback could keep sampling active or interfere with probing. The
  implementation must explicitly stop after the query.

## Rollback
If Klipper fails to start or the query behaves badly:

```bash
sudo systemctl stop klipper
cp ~/klipper/klippy/extras/probe_eddy_current.py.bak.<timestamp> \
   ~/klipper/klippy/extras/probe_eddy_current.py
sudo systemctl start klipper
```

Then verify:

```bash
systemctl is-active klipper
tail -n 80 ~/printer_data/logs/klippy.log
```

## Documentation follow-ups
- Update `new_config/beacon.cfg` to remove or rename stale Beacon macros such as `CHECK_Z`,
  `CHECK_BACKLASH`, and `AUTO_BEACON_CALIBRATE`.
- Add a worklog entry if the Klipper host patch is implemented and verified.
- Save a patch file under `doc/` or `klipper-patches/` so the change can be reapplied after
  future Klipper updates.
