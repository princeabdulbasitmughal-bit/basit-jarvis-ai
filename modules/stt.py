"""
============================================================
MODULE 2: SPEECH-TO-TEXT (Real-Time Whisper / Vosk)
============================================================
Handles microphone capture with dynamic silence detection
and transcribes speech to text using faster-whisper or local models.
"""

import io
import time
import wave
import logging
import numpy as np
from typing import Optional

logger = logging.getLogger("Jarvis.STT")


class SpeechToText:
    def __init__(
        self,
        model_size: str = "base",
        device: str = "cpu",
        compute_type: str = "int8",
        language: str = "en",
        silence_threshold: int = 450,
        silence_duration: float = 1.3
    ):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.language = language
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        self._model = None
        # Model is lazy-loaded on first transcribe() call to guarantee 0ms startup delay

    def _init_model(self):
        """Lazy-loads faster-whisper model on first use."""
        if self._model is not None:
            return
        try:
            from faster_whisper import WhisperModel
            logger.info(f"Loading faster-whisper ({self.model_size}) on {self.device} ({self.compute_type})...")
            self._model = WhisperModel(self.model_size, device=self.device, compute_type=self.compute_type)
            logger.info("faster-whisper model loaded successfully.")
        except Exception as e:
            logger.warning(f"faster-whisper could not be loaded: {e}. Fallback transcription active.")
            self._model = None

    def record_until_silence(self, max_duration: float = 10.0, sample_rate: int = 16000) -> Optional[np.ndarray]:
        """
        Records audio from microphone until user stops speaking (silence detected).
        Returns numpy int16 audio array.
        """
        try:
            import sounddevice as sd
        except ImportError:
            logger.error("sounddevice is not installed. Cannot capture mic.")
            return None

        logger.info("Listening for command...")
        chunk_size = 1024
        silence_chunks_limit = int((self.silence_duration * sample_rate) / chunk_size)

        recorded_chunks = []
        silent_chunks = 0
        speech_started = False
        start_time = time.time()

        try:
            with sd.InputStream(samplerate=sample_rate, channels=1, dtype="int16", blocksize=chunk_size) as stream:
                while time.time() - start_time < max_duration:
                    data, overflow = stream.read(chunk_size)
                    if overflow:
                        continue

                    # Calculate Root Mean Square (RMS) energy
                    energy = np.sqrt(np.mean(data.astype(np.float32) ** 2))

                    if energy > self.silence_threshold:
                        speech_started = True
                        silent_chunks = 0
                        recorded_chunks.append(data.copy())
                    else:
                        if speech_started:
                            recorded_chunks.append(data.copy())
                            silent_chunks += 1
                            if silent_chunks >= silence_chunks_limit:
                                logger.debug("Silence detected after speech, stopping recording.")
                                break
                        else:
                            # Keep tiny rolling buffer of pre-speech
                            if len(recorded_chunks) < 3:
                                recorded_chunks.append(data.copy())
                            else:
                                recorded_chunks.pop(0)
                                recorded_chunks.append(data.copy())

            if not speech_started or not recorded_chunks:
                logger.info("No speech detected.")
                return None

            return np.concatenate(recorded_chunks, axis=0).flatten()

        except Exception as e:
            logger.error(f"Error during audio recording: {e}")
            return None

    def transcribe(self, audio_data: np.ndarray, sample_rate: int = 16000) -> str:
        """
        Converts audio array into text using Whisper.
        """
        if audio_data is None or len(audio_data) == 0:
            return ""

        if self._model is not None:
            try:
                # faster-whisper accepts float32 normalized between -1.0 and 1.0
                audio_float = audio_data.astype(np.float32) / 32768.0
                segments, info = self._model.transcribe(
                    audio_float,
                    language=self.language,
                    beam_size=5,
                    vad_filter=True
                )
                text = " ".join([seg.text for seg in segments]).strip()
                logger.info(f"Transcribed: '{text}' (lang={info.language}, prob={info.language_probability:.2f})")
                return text
            except Exception as e:
                logger.error(f"Transcription failed: {e}")
                return ""
        else:
            logger.warning("No STT model loaded to transcribe audio.")
            return ""

    def listen_and_transcribe(self, max_duration: float = 10.0) -> str:
        """Helper to record and transcribe in one call."""
        audio = self.record_until_silence(max_duration=max_duration)
        if audio is not None:
            return self.transcribe(audio)
        return ""
