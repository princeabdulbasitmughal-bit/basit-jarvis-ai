"""
================================================================================
👑 BASIT JARVIS AI — KOKORO NEURAL TTS ENGINE
================================================================================
Replaces pyttsx3 robotic voice with Kokoro-82M ultra-realistic neural TTS.
Fallback chain: Kokoro-82M -> modules.tts (pyttsx3 COM-isolated) -> silent
================================================================================
"""

import os
import sys
import threading
import queue
import time
import logging

# Ensure UTF-8 output encoding for Windows terminals
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

logger = logging.getLogger("Jarvis.KokoroTTS")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── TTS speak queue (non-blocking) ──────────────────────────────────────────
_tts_queue = queue.Queue()
_tts_thread = None
_kokoro_model = None
_kokoro_available = False
_voice_speed = 1.0
_voice_enabled = True


def _init_kokoro():
    """Try to load Kokoro-82M ONNX model."""
    global _kokoro_model, _kokoro_available
    try:
        from kokoro_onnx import Kokoro
        model_path = os.path.join(BASE_DIR, "models", "kokoro-v0_19.onnx")
        voices_path = os.path.join(BASE_DIR, "models", "voices.bin")

        if not os.path.exists(model_path) or not os.path.exists(voices_path):
            logger.info("[KOKORO] Model files not present locally — fallback to modules.tts")
            _kokoro_available = False
            return

        _kokoro_model = Kokoro(model_path, voices_path)
        _kokoro_available = True
        logger.info("[KOKORO] [OK] Neural TTS loaded — ultra-realistic voice ACTIVE")
    except ImportError:
        logger.info("[KOKORO] kokoro-onnx not installed — fallback to modules.tts")
        _kokoro_available = False
    except Exception as e:
        logger.warning(f"[KOKORO] Failed to load: {e}")
        _kokoro_available = False


def _speak_kokoro(text: str) -> bool:
    """Speak using Kokoro-82M neural TTS."""
    try:
        import sounddevice as sd
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
        logger.error(f"[KOKORO] Speak error: {e}")
        return False


def _speak_pyttsx3(text: str) -> bool:
    """Speak using unified modules.tts fallback."""
    try:
        from modules.tts import get_tts
        get_tts().speak(text, block=True)
        return True
    except Exception as e:
        logger.error(f"[PYTTSX3 FALLBACK] Speak error: {e}")
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

            # Try Kokoro first, then pyttsx3 fallback
            success = False
            if _kokoro_available and _kokoro_model:
                success = _speak_kokoro(text)
            if not success:
                _speak_pyttsx3(text)

            _tts_queue.task_done()
        except queue.Empty:
            continue
        except Exception as e:
            logger.error(f"[TTS WORKER] Error: {e}")


def speak(text: str, blocking: bool = False):
    """
    Speak text using Jarvis voice engine.
    
    Args:
        text: Text to speak
        blocking: Wait for speech to complete (default: False = non-blocking)
    """
    if not text or not _voice_enabled:
        return

    # Clean text for TTS
    clean = _clean_for_tts(text)
    if not clean.strip():
        return

    if blocking:
        if _kokoro_available and _kokoro_model:
            success = _speak_kokoro(clean)
            if not success:
                _speak_pyttsx3(clean)
        else:
            _speak_pyttsx3(clean)
    else:
        _tts_queue.put(clean)


def _clean_for_tts(text: str) -> str:
    """Remove emojis, markdown, and special formatting from TTS text."""
    from modules.tts import clean_text_for_speech
    return clean_text_for_speech(text)


def set_voice_enabled(enabled: bool):
    """Enable or disable TTS voice output."""
    global _voice_enabled
    _voice_enabled = enabled
    status = "ENABLED" if enabled else "MUTED"
    logger.info(f"[KOKORO TTS] Voice {status}")


def set_speed(speed: float):
    """Set TTS speed (0.5 = slow, 1.0 = normal, 1.5 = fast)."""
    global _voice_speed
    _voice_speed = max(0.3, min(2.0, speed))


def get_status() -> dict:
    """Return TTS engine status."""
    return {
        "engine": "kokoro-82M" if _kokoro_available else "pyttsx3",
        "kokoro_available": _kokoro_available,
        "pyttsx3_available": True,
        "voice_enabled": _voice_enabled,
        "speed": _voice_speed,
        "queue_size": _tts_queue.qsize()
    }


def init_tts():
    """Initialize TTS engine and start background worker thread."""
    global _tts_thread

    # Try Kokoro first (non-blocking init)
    kokoro_thread = threading.Thread(target=_init_kokoro, daemon=True, name="KokoroInit")
    kokoro_thread.start()

    # Start TTS worker thread if not already running
    if _tts_thread is None or not _tts_thread.is_alive():
        _tts_thread = threading.Thread(target=_tts_worker, daemon=True, name="JarvisKokoroWorker")
        _tts_thread.start()
    logger.info("[KOKORO TTS] TTS engine initialized — worker running")


def shutdown_tts():
    """Gracefully shut down TTS engine."""
    _tts_queue.put(None)
    if _tts_thread:
        _tts_thread.join(timeout=3)
    logger.info("[KOKORO TTS] Shutdown complete")


# Auto-initialize on import
init_tts()
