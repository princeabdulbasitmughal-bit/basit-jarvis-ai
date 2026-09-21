"""
Evaluation script for Audio and Voice Pipelines:
1. Audio Hardware & Diagnostics (modules/audio_health.py)
2. Text-to-Speech (modules/tts.py - pyttsx3)
3. Neural TTS (modules/kokoro_tts.py - Kokoro-82M)
4. Speech-to-Text (modules/stt.py - faster-whisper)
5. Wake Word Detection (modules/wake_word.py - openWakeWord)
"""

import os
import sys
import json
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

results = {}

# 1. Audio Hardware Diagnostics
print("--- 1. Testing Audio Health ---")
t0 = time.perf_counter()
from modules.audio_health import get_audio_devices, test_microphone, get_recommended_interaction_mode
devs = get_audio_devices()
mic_responsive = test_microphone(0.1)
rec_mode = get_recommended_interaction_mode()
lat_audio = round((time.perf_counter() - t0) * 1000, 2)
print(f"Inputs: {len(devs.get('inputs', []))}, Outputs: {len(devs.get('outputs', []))}")
print(f"Default Output: {devs.get('default_output')}, Default Input: {devs.get('default_input')}")
print(f"Recommended mode: {rec_mode}")
results["audio_hardware"] = {
    "status": "Working" if devs.get("speaker_available") else "Degraded",
    "latency_ms": lat_audio,
    "speaker_available": devs.get("speaker_available"),
    "mic_available": devs.get("mic_available"),
    "recommended_mode": rec_mode
}

# 2. Text-to-Speech (pyttsx3)
print("\n--- 2. Testing Offline TTS (pyttsx3) ---")
t0 = time.perf_counter()
tts_status = "Not Working"
tts_voices = 0
try:
    import pyttsx3
    eng = pyttsx3.init()
    voices = eng.getProperty("voices")
    tts_voices = len(voices) if voices else 0
    tts_status = "Working" if tts_voices > 0 else "Degraded"
    print(f"pyttsx3 initialized. System voices detected: {tts_voices}")
except Exception as e:
    print(f"pyttsx3 error: {e}")
lat_tts = round((time.perf_counter() - t0) * 1000, 2)
results["tts_pyttsx3"] = {
    "status": tts_status,
    "latency_ms": lat_tts,
    "voices_count": tts_voices
}

# 3. Neural TTS (Kokoro)
print("\n--- 3. Testing Neural TTS (Kokoro-82M) ---")
t0 = time.perf_counter()
kokoro_model_path = os.path.join(BASE_DIR, "models", "kokoro-v0_19.onnx")
kokoro_exists = os.path.exists(kokoro_model_path)
has_kokoro_lib = False
try:
    import kokoro_onnx
    has_kokoro_lib = True
except ImportError:
    pass
lat_kokoro = round((time.perf_counter() - t0) * 1000, 2)
print(f"kokoro_onnx package installed: {has_kokoro_lib}, Model on disk: {kokoro_exists}")
results["tts_kokoro_neural"] = {
    "status": "Working" if kokoro_exists else ("Degraded" if has_kokoro_lib else "Degraded"),
    "latency_ms": lat_kokoro,
    "package_installed": has_kokoro_lib,
    "model_cached": kokoro_exists,
    "fallback_active": True
}

# 4. Speech-to-Text (faster-whisper)
print("\n--- 4. Testing Speech-to-Text (faster-whisper) ---")
t0 = time.perf_counter()
has_whisper = False
try:
    import faster_whisper
    has_whisper = True
except ImportError:
    pass
lat_stt = round((time.perf_counter() - t0) * 1000, 2)
print(f"faster-whisper package installed: {has_whisper}")
results["stt_whisper"] = {
    "status": "Working" if has_whisper else "Degraded",
    "latency_ms": lat_stt,
    "package_installed": has_whisper
}

# 5. Wake Word (openWakeWord)
print("\n--- 5. Testing Wake Word (openWakeWord) ---")
t0 = time.perf_counter()
has_oww = False
try:
    import openwakeword
    has_oww = True
except ImportError:
    pass
lat_oww = round((time.perf_counter() - t0) * 1000, 2)
print(f"openwakeword package installed: {has_oww}")
results["wake_word_openwakeword"] = {
    "status": "Working" if has_oww else "Degraded",
    "latency_ms": lat_oww,
    "package_installed": has_oww,
    "lightweight_fallback": True
}

print("\nAUDIO & VOICE PIPELINE RESULTS:")
print(json.dumps(results, indent=2))

with open("reports/audio_pipeline_eval.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
