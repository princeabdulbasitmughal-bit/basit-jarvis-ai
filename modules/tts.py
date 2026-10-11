"""
============================================================
👑 BASIT JARVIS AI — MODULE 5: TEXT-TO-SPEECH (TTS)
============================================================
Provides voice response for Jarvis:
- pyttsx3 (100% offline, zero-lag, customizable rate & voice)
- Auto-detects Microsoft David Desktop & Microsoft Zira Desktop
- Non-blocking threaded audio playback queue with zero COM deadlocks
- Full text sanitization (strips markdown, emojis, asterisks, URLs)
- Seamless mute / unmute / volume synchronization
============================================================
"""

import os
import sys
import re
import queue
import logging
import threading
from typing import Optional, List, Dict, Any

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

logger = logging.getLogger("Jarvis.TTS")


def clean_text_for_speech(text: str) -> str:
    """Removes emojis, markdown, URLs, and special formatting for clean speech."""
    if not text:
        return ""
    # Remove code blocks
    text = re.sub(r'```.*?```', 'code block omitted', text, flags=re.DOTALL)
    text = re.sub(r'`(.*?)`', r'\1', text)
    # Remove markdown bold/italic
    text = re.sub(r'\*{1,3}(.*?)\*{1,3}', r'\1', text)
    text = re.sub(r'_{1,3}(.*?)_{1,3}', r'\1', text)
    # Remove URLs
    text = re.sub(r'http[s]?://\S+', 'link', text)
    # Remove emojis & non-standard symbols
    emoji_pattern = re.compile(
        "["
        r"\U0001F600-\U0001F64F"  # emoticons
        r"\U0001F300-\U0001F5FF"  # symbols & pictographs
        r"\U0001F680-\U0001F6FF"  # transport & map
        r"\U0001F1E0-\U0001F1FF"  # flags
        r"\U00002702-\U000027B0"
        r"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE
    )
    text = emoji_pattern.sub('', text)
    # Clean whitespace
    return re.sub(r'\s+', ' ', text).strip()


class TextToSpeech:
    """
    Industrial-grade, zero-hang TTS manager for Basit Jarvis AI.
    Runs speech synthesis on a dedicated background worker thread with COM isolation.
    """
    def __init__(
        self,
        engine: str = "pyttsx3",
        voice_index: int = 0,
        rate: int = 180,
        volume: float = 0.95,
        elevenlabs_api_key: str = "",
        elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"
    ):
        self.engine_name = engine
        self.voice_index = voice_index
        self.rate = rate
        self.volume = volume
        self.elevenlabs_api_key = elevenlabs_api_key
        self.elevenlabs_voice_id = elevenlabs_voice_id

        self._queue = queue.Queue()
        self._running = True
        self._speaking = False
        self.muted = False
        self.active_voice_name = "Microsoft David"
        
        # Start isolated worker thread
        self._worker_thread = threading.Thread(target=self._speech_worker, daemon=True, name="TTSWorker")
        self._worker_thread.start()

    @property
    def is_speaking(self) -> bool:
        return self._speaking

    def mute(self):
        """Mutes speech output."""
        self.muted = True
        logger.info("[TTS] Jarvis voice muted.")

    def unmute(self):
        """Unmutes speech output."""
        self.muted = False
        logger.info("[TTS] Jarvis voice unmuted.")

    def toggle_mute(self) -> bool:
        """Toggles TTS speech mute status."""
        self.muted = not self.muted
        logger.info(f"[TTS] Jarvis voice mute toggled: {self.muted}")
        return self.muted

    def set_rate(self, rate: int):
        """Sets speech rate (words per minute, default ~180)."""
        self.rate = max(100, min(350, int(rate)))

    def set_volume(self, volume: float):
        """Sets speech volume (0.0 to 1.0)."""
        self.volume = max(0.0, min(1.0, float(volume)))

    def get_available_voices(self) -> List[Dict[str, Any]]:
        """Returns list of all available voices on system."""
        voices_list = []
        try:
            import pyttsx3
            eng = pyttsx3.init()
            for idx, v in enumerate(eng.getProperty("voices")):
                voices_list.append({
                    "index": idx,
                    "id": v.id,
                    "name": v.name,
                    "languages": getattr(v, "languages", ["en-US"]),
                    "gender": getattr(v, "gender", "unknown")
                })
        except Exception as e:
            logger.warning(f"[TTS] Voice discovery error: {e}")
            voices_list = [
                {"index": 0, "id": "david", "name": "Microsoft David Desktop", "gender": "male"},
                {"index": 1, "id": "zira", "name": "Microsoft Zira Desktop", "gender": "female"}
            ]
        return voices_list

    def set_voice(self, voice_identifier: Any) -> bool:
        """Sets active voice by index (0, 1) or name/id substring ('zira', 'david')."""
        try:
            voices = self.get_available_voices()
            if isinstance(voice_identifier, int) and 0 <= voice_identifier < len(voices):
                self.voice_index = voice_identifier
                self.active_voice_name = voices[voice_identifier]["name"]
                logger.info(f"[TTS] Switched voice to index {self.voice_index}: {self.active_voice_name}")
                return True
            ident = str(voice_identifier).lower()
            for v in voices:
                if ident in v["name"].lower() or ident in v["id"].lower():
                    self.voice_index = v["index"]
                    self.active_voice_name = v["name"]
                    logger.info(f"[TTS] Switched voice to {self.active_voice_name}")
                    return True
        except Exception as e:
            logger.error(f"[TTS] Error changing voice: {e}")
        return False

    def speak(self, text: str, block: bool = False):
        """Queues text to be spoken by Jarvis."""
        if not text:
            return
        cleaned = clean_text_for_speech(text)
        if not cleaned:
            return
        if self.muted:
            logger.info(f"[MUTED TTS] Jarvis: \"{cleaned}\"")
            return

        if block:
            done_event = threading.Event()
            self._queue.put((cleaned, done_event))
            done_event.wait(timeout=15.0)
        else:
            self._queue.put((cleaned, None))

    def stop(self):
        """Stops worker."""
        self._running = False
        self._queue.put((None, None))

    def _speech_worker(self):
        """Dedicated worker thread for isolated COM/SAPI5 execution."""
        # Initialize COM in this worker thread if on Windows
        try:
            import pythoncom
            pythoncom.CoInitialize()
        except Exception:
            pass

        pyttsx3_engine = None
        try:
            import pyttsx3
            pyttsx3_engine = pyttsx3.init()
            pyttsx3_engine.setProperty("rate", self.rate)
            pyttsx3_engine.setProperty("volume", self.volume)
            voices = pyttsx3_engine.getProperty("voices")
            if voices and self.voice_index < len(voices):
                pyttsx3_engine.setProperty("voice", voices[self.voice_index].id)
                self.active_voice_name = voices[self.voice_index].name
            logger.info(f"[TTS] Engine initialized with voice: {self.active_voice_name}")
        except Exception as e:
            logger.warning(f"[TTS] pyttsx3 init error in worker: {e}")

        while self._running:
            try:
                item = self._queue.get(timeout=0.5)
            except queue.Empty:
                continue

            text, done_event = item
            if text is None:
                break

            self._speaking = True
            try:
                if pyttsx3_engine is not None:
                    # Update parameters dynamically
                    pyttsx3_engine.setProperty("rate", self.rate)
                    pyttsx3_engine.setProperty("volume", self.volume)
                    voices = pyttsx3_engine.getProperty("voices")
                    if voices and 0 <= self.voice_index < len(voices):
                        pyttsx3_engine.setProperty("voice", voices[self.voice_index].id)
                    pyttsx3_engine.say(text)
                    pyttsx3_engine.runAndWait()
                else:
                    print(f"[JARVIS VOICE]: {text}", flush=True)
            except Exception as e:
                logger.error(f"[TTS] Error during speech synthesis: {e}")
                # Try recreating engine on error
                try:
                    import pyttsx3
                    pyttsx3_engine = pyttsx3.init()
                except Exception:
                    pass
            finally:
                self._speaking = False
                if done_event is not None:
                    done_event.set()
                self._queue.task_done()


# Global Singleton Instance
_global_tts_instance: Optional[TextToSpeech] = None

def get_tts() -> TextToSpeech:
    """Returns the shared global TextToSpeech instance."""
    global _global_tts_instance
    if _global_tts_instance is None:
        _global_tts_instance = TextToSpeech()
    return _global_tts_instance
