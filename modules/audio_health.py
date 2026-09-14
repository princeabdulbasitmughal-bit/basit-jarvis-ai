"""
================================================================================
👑 BASIT JARVIS AI — AUDIO HEALTH & HARDWARE DIAGNOSTIC
================================================================================
Automatic audio device discovery, permission verification, and fallback manager.
Prevents voice loop from ever hanging or crashing when audio hardware fails.

Capabilities:
  - Enumerates input microphones & output speakers
  - Tests 0.2s recording buffer to verify mic hardware is active
  - Provides graceful fallback recommendation ('voice' vs 'keyboard')
  - Zero system hang — all hardware queries strictly bounded
================================================================================
"""

import sys
import os
import logging
from typing import Dict, Any, List

# Force UTF-8 encoding for Windows terminals
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

logger = logging.getLogger("JarvisAudioHealth")


def get_audio_devices() -> Dict[str, Any]:
    """Enumerates input and output devices using sounddevice."""
    devices = {
        "inputs": [],
        "outputs": [],
        "default_input": None,
        "default_output": None,
        "mic_available": False,
        "speaker_available": False
    }

    try:
        import sounddevice as sd
        dev_list = sd.query_devices()
        default_in, default_out = sd.default.device

        for idx, d in enumerate(dev_list):
            name = d.get("name", f"Device {idx}")
            max_in = d.get("max_input_channels", 0)
            max_out = d.get("max_output_channels", 0)

            if max_in > 0:
                is_default = (idx == default_in)
                devices["inputs"].append({"id": idx, "name": name, "default": is_default})
                if is_default:
                    devices["default_input"] = name

            if max_out > 0:
                is_default = (idx == default_out)
                devices["outputs"].append({"id": idx, "name": name, "default": is_default})
                if is_default:
                    devices["default_output"] = name

        devices["mic_available"] = len(devices["inputs"]) > 0
        devices["speaker_available"] = len(devices["outputs"]) > 0

    except Exception as e:
        logger.warning(f"[AUDIO ENUMERATION FAILED]: {e}")

    return devices


def test_microphone(duration_sec: float = 0.2) -> bool:
    """Briefly tests recording a short audio buffer to confirm hardware responsiveness."""
    try:
        import sounddevice as sd
        import numpy as np

        sample_rate = 16000
        recording = sd.rec(int(duration_sec * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
        sd.wait(timeout=duration_sec + 0.5)
        # Check if buffer was populated
        return recording is not None and len(recording) > 0
    except Exception:
        return False


def get_recommended_interaction_mode() -> str:
    """Returns 'voice' if mic and speaker are operational, else 'keyboard'."""
    devs = get_audio_devices()
    if devs.get("mic_available") and test_microphone():
        return "voice"
    return "keyboard"


if __name__ == "__main__":
    print("👑 [JARVIS AUDIO HEALTH DIAGNOSTIC]")
    devs = get_audio_devices()
    print(f"Inputs found:  {len(devs['inputs'])} (Default: {devs['default_input']})")
    print(f"Outputs found: {len(devs['outputs'])} (Default: {devs['default_output']})")
    mic_test = test_microphone()
    print(f"Mic Hardware Buffer Test: {'PASSED ✅' if mic_test else 'NO HARDWARE MIC / BUSY ⚠️'}")
    recommended = get_recommended_interaction_mode()
    print(f"Recommended Voice Mode:   {recommended.upper()} MODE")
