"""
============================================================
MODULE 10: SECURITY LAYER (Voice Auth & Sensitive Action Guards)
============================================================
Provides:
1. Sensitive Action Guards: Intercepts delete/shutdown/restart and requires confirmation.
2. Voice Authentication: Speaker verification using audio acoustic features (MFCCs).
"""

import os
import time
import logging
import numpy as np
from typing import Optional, List, Callable

logger = logging.getLogger("Jarvis.Security")


class SecurityLayer:
    def __init__(
        self,
        voice_auth_enabled: bool = False,
        voice_auth_threshold: float = 0.75,
        sensitive_commands: Optional[List[str]] = None,
        require_confirmation: bool = True,
        voice_profile_path: Optional[str] = None
    ):
        self.voice_auth_enabled = voice_auth_enabled
        self.voice_auth_threshold = voice_auth_threshold
        self.sensitive_commands = sensitive_commands or [
            "delete", "shutdown", "restart", "format", "remove", "kill", "wipe"
        ]
        self.require_confirmation = require_confirmation
        self.voice_profile_path = voice_profile_path or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "basit_voice_profile.npy"
        )

        self._pending_confirmation: Optional[dict] = None
        self._pending_timestamp: float = 0.0

    def is_sensitive(self, intent_or_text: str) -> bool:
        """Checks if a command or intent is categorized as sensitive."""
        lower = intent_or_text.lower()
        return any(sens in lower for sens in self.sensitive_commands)

    def request_confirmation(self, command_info: dict, prompt_callback: Optional[Callable[[str], None]] = None) -> str:
        """Registers a command requiring confirmation and prompts user."""
        self._pending_confirmation = command_info
        self._pending_timestamp = time.time()
        msg = "This is a sensitive system action, sir. Please say 'confirm' to execute, or 'cancel' to abort."
        if prompt_callback:
            prompt_callback(msg)
        return msg

    def check_confirmation(self, user_response: str) -> Optional[dict]:
        """Validates confirmation response within a 15-second window."""
        if not self._pending_confirmation:
            return None

        if time.time() - self._pending_timestamp > 15.0:
            logger.info("Pending sensitive action confirmation timed out.")
            self._pending_confirmation = None
            return None

        resp = user_response.lower().strip()
        if "confirm" in resp or "yes" in resp or "proceed" in resp or "do it" in resp:
            action = self._pending_confirmation
            self._pending_confirmation = None
            return action
        elif "cancel" in resp or "no" in resp or "abort" in resp or "stop" in resp:
            logger.info("Sensitive action cancelled by user.")
            self._pending_confirmation = None
            return None

        return None

    # ---------------------------------------------------------
    # 2. VOICE BIOMETRICS / SPEAKER AUTHENTICATION
    # ---------------------------------------------------------
    def verify_voice(self, audio_data: np.ndarray, sample_rate: int = 16000) -> bool:
        """
        Verifies if current speaker matches Basit's voice profile.
        Returns True if voice matches or if auth is disabled.
        """
        if not self.voice_auth_enabled:
            return True

        if not os.path.exists(self.voice_profile_path):
            logger.warning("Voice auth enabled but no profile enrolled. Enrolling current voice.")
            self.enroll_voice(audio_data, sample_rate)
            return True

        current_features = self._extract_features(audio_data, sample_rate)
        if current_features is None:
            return False

        try:
            saved_profile = np.load(self.voice_profile_path)
            # Cosine similarity
            dot = np.dot(current_features, saved_profile)
            norm_a = np.linalg.norm(current_features)
            norm_b = np.linalg.norm(saved_profile)
            if norm_a == 0 or norm_b == 0:
                return False
            similarity = dot / (norm_a * norm_b)
            logger.info(f"Speaker verification similarity: {similarity:.3f} (Threshold: {self.voice_auth_threshold})")
            return similarity >= self.voice_auth_threshold
        except Exception as e:
            logger.error(f"Voice verification error: {e}")
            return False

    def enroll_voice(self, audio_data: np.ndarray, sample_rate: int = 16000) -> bool:
        """Enrolls Basit's voice profile."""
        features = self._extract_features(audio_data, sample_rate)
        if features is not None:
            np.save(self.voice_profile_path, features)
            logger.info(f"Enrolled owner voice profile to {self.voice_profile_path}")
            return True
        return False

    def _extract_features(self, audio_data: np.ndarray, sample_rate: int) -> Optional[np.ndarray]:
        """Extracts acoustic spectral energy features."""
        try:
            # Simple FFT-based spectral centroid & energy distribution
            if len(audio_data) < sample_rate:
                return None
            spectrum = np.abs(np.fft.rfft(audio_data[:sample_rate * 2]))
            # 64-bin spectral energy summary
            bins = np.array_split(spectrum, 64)
            features = np.array([np.mean(b) for b in bins], dtype=np.float32)
            norm = np.linalg.norm(features)
            return features / (norm + 1e-8)
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            return None
