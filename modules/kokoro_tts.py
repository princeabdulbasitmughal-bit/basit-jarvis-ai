"""
================================================================================
👑 BASIT JARVIS AI — KOKORO NEURAL TTS ENGINE
================================================================================
Replaces pyttsx3 robotic voice with Kokoro-82M ultra-realistic neural TTS.
Fallback chain: Kokoro-82M → pyttsx3 → silent (no crash)

Install: pip install kokoro-onnx soundfile sounddevice
Model:   hexgrad/Kokoro-82M (MIT license, runs 100% locally)
================================================================================
"""

import os
import sys
import threading
import queue
import tempfile
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── TTS speak queue (non-blocking) ──────────────────────────────────────────
_tts_queue = queue.Queue()
_tts_thread = None
_kokoro_model = None
_kokoro_available = False
_pyttsx3_engine = None
_voice_speed = 1.0
_voice_enabled = True


def _init_kokoro():
    """Try to load Kokoro-82M ONNX model."""
    global _kokoro_model, _kokoro_available
    try:
        from kokoro_onnx import Kokoro
        model_path = os.path.join(BASE_DIR, "models", "kokoro-v0_19.onnx")
        voices_path = os.path.join(BASE_DIR, "models", "voices.bin")

        # Download if not present
        if not os.path.exists(model_path):
            print("[KOKORO] Model not found locally — downloading from HuggingFace...")
            _download_kokoro_model(model_path, voices_path)

        if os.path.exists(model_path) and os.path.exists(voices_path):
            _kokoro_model = Kokoro(model_path, voices_path)
            _kokoro_available = True
            print("[KOKORO] ✅ Neural TTS loaded — ultra-realistic voice ACTIVE")
        else:
            print("[KOKORO] ⚠️  Model files not found — falling back to pyttsx3")
    except ImportError:
        print("[KOKORO] kokoro-onnx not installed — pip install kokoro-onnx")
    except Exception as e:
        print(f"[KOKORO] Failed to load: {e}")


def _download_kokoro_model(model_path, voices_path):
    """Download Kokoro model from HuggingFace."""
    try:
        import urllib.request
        os.makedirs(os.path.dirname(model_path), exist_ok=True)

        model_url = "https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/kokoro-v0_19.onnx"
        voices_url = "https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/voices.bin"

        print("[KOKORO] Downloading model (~83MB)...")
        urllib.request.urlretrieve(model_url, model_path)
        print("[KOKORO] Downloading voices (~24MB)...")
        urllib.request.urlretrieve(voices_url, voices_path)
        print("[KOKORO] ✅ Download complete!")
    except Exception as e:
        print(f"[KOKORO] Download failed: {e}")


def _init_pyttsx3_fallback():
    """Initialize pyttsx3 as fallback TTS."""
    global _pyttsx3_engine
    try:
        import pyttsx3
        _pyttsx3_engine = pyttsx3.init()
        _pyttsx3_engine.setProperty('rate', 175)
        _pyttsx3_engine.setProperty('volume', 0.9)
        # Try to set a better voice
        voices = _pyttsx3_engine.getProperty('voices')
        for v in voices:
            if 'david' in v.name.lower() or 'english' in v.name.lower():
                _pyttsx3_engine.setProperty('voice', v.id)
                break
        print("[PYTTSX3] ✅ Fallback TTS ready")
    except Exception as e:
        print(f"[PYTTSX3] Fallback init failed: {e}")


def _speak_kokoro(text: str):
    """Speak using Kokoro-82M neural TTS."""
    try:
        import sounddevice as sd
        import soundfile as sf
        import numpy as np

        samples, sample_rate = _kokoro_model.create(
            text,
            voice="af",        # American Female — natural sounding
            speed=_voice_speed,
            lang="en-us"
        )
        sd.play(samples, sample_rate)
        sd.wait()
        return True
    except Exception as e:
        print(f"[KOKORO] Speak error: {e}")
        return False


def _speak_pyttsx3(text: str):
    """Speak using pyttsx3 fallback."""
    global _pyttsx3_engine
    try:
        if _pyttsx3_engine is None:
            _init_pyttsx3_fallback()
        if _pyttsx3_engine:
            _pyttsx3_engine.say(text)
            _pyttsx3_engine.runAndWait()
            return True
    except Exception as e:
        print(f"[PYTTSX3] Speak error: {e}")
        # Reinitialize on error
        _pyttsx3_engine = None
    return False


def _tts_worker():
    """Background TTS worker thread — processes speak queue."""
    while True:
        try:
            text = _tts_queue.get(timeout=1)
            if text is None:  # Shutdown signal
                break
            if not _voice_enabled:
                _tts_queue.task_done()
                continue

            # Try Kokoro first, then pyttsx3
            success = False
            if _kokoro_available and _kokoro_model:
                success = _speak_kokoro(text)
            if not success:
                _speak_pyttsx3(text)

            _tts_queue.task_done()
        except queue.Empty:
            continue
        except Exception as e:
            print(f"[TTS WORKER] Error: {e}")


def speak(text: str, blocking: bool = False):
    """
    Speak text using Jarvis voice engine.
    
    Args:
        text: Text to speak
        blocking: Wait for speech to complete (default: False = non-blocking)
    """
    if not text or not _voice_enabled:
        return

    # Clean text for TTS (remove emoji, markdown)
    clean = _clean_for_tts(text)
    if not clean.strip():
        return

    if blocking:
        if _kokoro_available and _kokoro_model:
            _speak_kokoro(clean)
        else:
            _speak_pyttsx3(clean)
    else:
        _tts_queue.put(clean)


def _clean_for_tts(text: str) -> str:
    """Remove emojis, markdown, and special chars from TTS text."""
    import re
    # Remove emojis
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE
    )
    text = emoji_pattern.sub('', text)
    # Remove markdown bold/italic
    text = re.sub(r'\*{1,3}(.*?)\*{1,3}', r'\1', text)
    text = re.sub(r'`(.*?)`', r'\1', text)
    # Remove URLs
    text = re.sub(r'http\S+', 'link', text)
    return text.strip()


def set_voice_enabled(enabled: bool):
    """Enable or disable TTS voice output."""
    global _voice_enabled
    _voice_enabled = enabled
    status = "ENABLED" if enabled else "MUTED"
    print(f"[KOKORO TTS] Voice {status}")


def set_speed(speed: float):
    """Set TTS speed (0.5 = slow, 1.0 = normal, 1.5 = fast)."""
    global _voice_speed
    _voice_speed = max(0.3, min(2.0, speed))


def get_status() -> dict:
    """Return TTS engine status."""
    return {
        "engine": "kokoro-82M" if _kokoro_available else "pyttsx3",
        "kokoro_available": _kokoro_available,
        "pyttsx3_available": _pyttsx3_engine is not None,
        "voice_enabled": _voice_enabled,
        "speed": _voice_speed,
        "queue_size": _tts_queue.qsize()
    }


def init_tts():
    """Initialize TTS engine and start background worker thread."""
    global _tts_thread

    # Try Kokoro first (non-blocking init)
    kokoro_thread = threading.Thread(target=_init_kokoro, daemon=True)
    kokoro_thread.start()

    # Initialize pyttsx3 fallback immediately
    _init_pyttsx3_fallback()

    # Start TTS worker thread
    _tts_thread = threading.Thread(target=_tts_worker, daemon=True, name="JarvisTTS")
    _tts_thread.start()
    print("[KOKORO TTS] 🎙️ TTS engine initialized — background worker running")


def shutdown_tts():
    """Gracefully shut down TTS engine."""
    _tts_queue.put(None)  # Signal worker to stop
    if _tts_thread:
        _tts_thread.join(timeout=3)
    print("[KOKORO TTS] Shutdown complete")


# ── Auto-initialize on import ──────────────────────────────────────────────
init_tts()
