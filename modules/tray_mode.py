"""
============================================================
MODULE 13: BACKGROUND / SYSTEM TRAY MODE (pystray)
============================================================
Runs Jarvis silently in the Windows system tray with status indicator,
mute/unmute toggles, manual trigger, and clean shutdown.
"""

import os
import sys
import logging
import threading
from typing import Callable, Optional

logger = logging.getLogger("Jarvis.Tray")


class SystemTrayApp:
    def __init__(
        self,
        on_trigger: Optional[Callable[[], None]] = None,
        on_toggle_mute: Optional[Callable[[], bool]] = None,
        on_exit: Optional[Callable[[], None]] = None
    ):
        self.on_trigger = on_trigger
        self.on_toggle_mute = on_toggle_mute
        self.on_exit = on_exit
        self.is_muted = False
        self._icon = None
        self._thread: Optional[threading.Thread] = None

    def start(self):
        """Starts system tray in a background thread."""
        self._thread = threading.Thread(target=self._run_tray, daemon=True, name="TrayThread")
        self._thread.start()
        logger.info("System tray initialized.")

    def stop(self):
        """Stops tray icon."""
        if self._icon:
            try:
                self._icon.stop()
            except Exception:
                pass

    def _create_icon_image(self):
        """Creates a programmatic 64x64 Jarvis blue arc-reactor icon."""
        try:
            from PIL import Image, ImageDraw
            img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            # Outer cyan glow ring
            draw.ellipse([4, 4, 60, 60], outline=(0, 200, 255, 255), width=4)
            # Inner circle
            draw.ellipse([16, 16, 48, 48], outline=(0, 255, 200, 255), width=3)
            # Center core
            draw.ellipse([26, 26, 38, 38], fill=(0, 255, 255, 255))
            return img
        except ImportError:
            return None

    def _run_tray(self):
        try:
            import pystray
            from pystray import MenuItem as item

            image = self._create_icon_image()
            if not image:
                logger.warning("PIL not installed. Cannot display tray icon.")
                return

            def on_trigger_clicked(icon, item):
                if self.on_trigger:
                    self.on_trigger()

            def on_dashboard_clicked(icon, item):
                import webbrowser
                webbrowser.open("http://localhost:8888")

            def on_mute_clicked(icon, item):
                if self.on_toggle_mute:
                    self.is_muted = self.on_toggle_mute()
                else:
                    self.is_muted = not self.is_muted

            def on_exit_clicked(icon, item):
                icon.stop()
                if self.on_exit:
                    self.on_exit()

            menu = pystray.Menu(
                item("Basit Jarvis AI (Active)", lambda i, it: None, enabled=False),
                pystray.Menu.SEPARATOR,
                item("🌐 Open Web Dashboard", on_dashboard_clicked),
                item("🎤 Trigger Voice Command", on_trigger_clicked),
                item(lambda text: "🔇 Unmute Wake Word" if self.is_muted else "🔊 Mute Wake Word", on_mute_clicked),
                pystray.Menu.SEPARATOR,
                item("❌ Exit Jarvis", on_exit_clicked)
            )

            self._icon = pystray.Icon("BasitJarvis", image, "Basit Jarvis AI", menu)
            self._icon.run()

        except Exception as e:
            logger.warning(f"Failed to start system tray icon: {e}")
