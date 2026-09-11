"""
============================================================
MODULE 5: TEXT-TO-SPEECH (TTS)
============================================================
Provides voice response for Jarvis:
- pyttsx3 (100% offline, zero-lag, customizable rate & voice)
- ElevenLabs API (optional, ultra-realistic voice synthesis)
- Non-blocking threaded audio playback queue
"""

import os
import queue
import logging
import threading
from typing import Optional

logger = logging.getLogger("Jarvis.TTS")


class TextToSpeech:
    def __init__(
        self,
        engine: str = "pyttsx3",
        voice_index: int = 0,
        rate: int = 175,
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
        self._worker_thread = threading.Thread(target=self._speech_worker, daemon=True, name="TTSWorker")
        self._worker_thread.start()

    @property
    def is_speaking(self) -> bool:
        return self._speaking

    def mute(self):
        """Mutes speech output."""
        self.muted = True
        logger.info("Jarvis TTS output muted.")

    def unmute(self):
        """Unmutes speech output."""
        self.muted = False
        logger.info("Jarvis TTS output unmuted.")

    def toggle_mute(self) -> bool:
        """Toggles TTS speech mute status."""
        self.muted = not self.muted
        logger.info(f"Jarvis TTS muted status: {self.muted}")
        return self.muted

    def speak(self, text: str, block: bool = False):
        """Queues text to be spoken by Jarvis."""
        text = text.strip()
        if not text:
            return
        if self.muted:
            logger.info(f"[MUTED TTS] Jarvis: \"{text}\"")
            print(f"[MUTED TTS]: {text}")
            return
        logger.info(f"Jarvis speaking: \"{text}\"")
        if block:
            self._speak_sync(text)
        else:
            self._queue.put(text)

    def stop(self):
        """Stops worker."""
        self._running = False
        self._queue.put(None)

    def _speech_worker(self):
        """Worker thread processing speech items in sequence."""
        # Initialize pyttsx3 engine in worker thread to prevent COM concurrency issues
        pyttsx3_engine = None
        try:
            import pyttsx3
            pyttsx3_engine = pyttsx3.init()
            pyttsx3_engine.setProperty("rate", self.rate)
            pyttsx3_engine.setProperty("volume", self.volume)
            voices = pyttsx3_engine.getProperty("voices")
            if voices and self.voice_index < len(voices):
                pyttsx3_engine.setProperty("voice", voices[self.voice_index].id)
            logger.info("pyttsx3 initialized successfully.")
        except Exception as e:
            logger.warning(f"pyttsx3 init error: {e}")

        while self._running:
            try:
                text = self._queue.get(timeout=0.5)
            except queue.Empty:
                continue

            if text is None:
                break

            self._speaking = True
            try:
                # 1. Check if ElevenLabs is configured and requested
                if self.engine_name == "elevenlabs" and self.elevenlabs_api_key:
                    self._speak_elevenlabs(text)
                elif pyttsx3_engine is not None:
                    pyttsx3_engine.say(text)
                    pyttsx3_engine.runAndWait()
                else:
                    # CLI audio fallback
                    print(f"[JARVIS VOICE]: {text}")
            except Exception as e:
                logger.error(f"Error speaking text '{text}': {e}")
            finally:
                self._speaking = False
                self._queue.task_done()

    def _speak_sync(self, text: str):
        """Direct synchronous speech."""
        try:
            import pyttsx3
            eng = pyttsx3.init()
            eng.setProperty("rate", self.rate)
            eng.setProperty("volume", self.volume)
            eng.say(text)
            eng.runAndWait()
        except Exception as e:
            print(f"[JARVIS VOICE]: {text}")

    def _speak_elevenlabs(self, text: str):
        """Synthesizes speech using ElevenLabs API and plays via sounddevice."""
        import requests
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.elevenlabs_voice_id}"
        headers = {
            "xi-api-key": self.elevenlabs_api_key,
            "Content-Type": "application/json"
        }
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
        }
        resp = requests.post(url, json=data, headers=headers, timeout=10)
        if resp.status_code == 200:
            import io
            import soundfile as sf
            import sounddevice as sd
            audio_data, sample_rate = sf.read(io.BytesIO(resp.content))
            sd.play(audio_data, sample_rate)
            sd.wait()
        else:
            logger.error(f"ElevenLabs error {resp.status_code}: {resp.text}")
