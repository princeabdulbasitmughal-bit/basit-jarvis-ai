"""
============================================================
MODULE 11: HOTKEY FALLBACK (Global Keyboard Shortcut)
============================================================
Provides an instant keyboard fallback (e.g., Ctrl+Shift+J)
to trigger Jarvis listening mode without saying the wake word.
"""

import logging
import threading
from typing import Callable, Optional

logger = logging.getLogger("Jarvis.Hotkey")


class HotkeyListener:
    def __init__(self, hotkey: str = "ctrl+shift+j", on_trigger: Optional[Callable[[], None]] = None):
        self.hotkey = hotkey.lower()
        self.on_trigger = on_trigger
        self._running = False
        self._hooked = False

    def start(self):
        """Hooks the global hotkey."""
        try:
            import keyboard
            keyboard.add_hotkey(self.hotkey, self._handle_press)
            self._running = True
            self._hooked = True
            logger.info(f"Global hotkey registered: [{self.hotkey.upper()}]")
        except Exception as e:
            logger.warning(f"Could not hook keyboard hotkey: {e}. Fallback interactive mode active.")
            self._hooked = False

    def stop(self):
        """Unhooks the hotkey."""
        if self._hooked:
            try:
                import keyboard
                keyboard.remove_hotkey(self.hotkey)
            except Exception:
                pass
            self._hooked = False
        self._running = False
        logger.info("Hotkey listener unhooked.")

    def _handle_press(self):
        logger.info(f"Hotkey [{self.hotkey.upper()}] pressed!")
        if self.on_trigger:
            try:
                self.on_trigger()
            except Exception as e:
                logger.error(f"Error in hotkey callback: {e}")
