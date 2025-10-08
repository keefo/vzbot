#!/usr/bin/env python3
import os, sys, shutil, subprocess, tempfile, pathlib

def cmd_exists(x): return shutil.which(x) is not None
def run(cmd, **kw):
    return subprocess.run(cmd, check=True, text=True, **kw)

def main():
    # Text comes from Klipper as command-line args after PARAMS=
    text = " ".join(sys.argv[1:]).strip()
    if not text:
        sys.exit(0)

    # Playback device: use Pulse if available, else your I2S card
    device = os.environ.get("DEVICE")
    if not device:
        if cmd_exists("pactl"):
            try:
                run(["pactl", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                device = "pulse"
            except Exception:
                device = "plughw:2,0"
        else:
            device = "plughw:2,0"

    lang   = os.environ.get("LANG_TTS", "en-US")
    gaindb = float(os.environ.get("GAIN_DB", "8"))  # software gain via sox
    piper_model = os.environ.get("PIPER_MODEL")     # set this env to use Piper

    # Temp WAV path
    tmpdir = pathlib.Path("/tmp")
    wav = tempfile.NamedTemporaryFile(prefix="speak_", suffix=".wav", dir=tmpdir, delete=False).name

    try:
        # Prefer Piper if model + binary exist
        if piper_model and pathlib.Path(piper_model).is_file() and cmd_exists("piper"):
            run(["piper", "--model", piper_model, "--output_file", wav], input=text)
        elif cmd_exists("pico2wave"):
            run(["pico2wave", "-l", lang, "-w", wav, text])
        elif cmd_exists("espeak-ng"):
            # -a amplitude (0-200), -s speed wpm
            run(["espeak-ng", "-v", lang.lower(), "-a", "200", "-s", "175", "-w", wav, text])
        else:
            # No TTS installed—fail gracefully
            sys.exit(0)

        # Normalize & boost if sox available
        if cmd_exists("sox") and gaindb != 0:
            loud = wav + ".loud.wav"
            run(["sox", wav, loud, "gain", "-n", str(gaindb)])
            os.replace(loud, wav)

        # Play it
        if device == "pulse":
            run(["aplay", "-D", "pulse", wav], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            run(["aplay", "-D", device, wav], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    finally:
        try: os.remove(wav)
        except Exception: pass

if __name__ == "__main__":
    main()

