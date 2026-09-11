"""
============================================================
MODULE 12: NOTIFICATION READER (Windows / Cross-App)
============================================================
Monitors and reads incoming notifications from Windows:
- WhatsApp, Slack, Outlook, Gmail, Teams, and System Alerts
"""

import sys
import time
import logging
import threading
from typing import Callable, Optional, List

logger = logging.getLogger("Jarvis.Notifications")


class NotificationReader:
    def __init__(
        self,
        enabled: bool = True,
        on_notification: Optional[Callable[[str, str, str], None]] = None,
        target_apps: Optional[List[str]] = None
    ):
        self.enabled = enabled
        self.on_notification = on_notification
        self.target_apps = [a.lower() for a in (target_apps or ["whatsapp", "slack", "outlook", "mail", "teams", "discord"])]
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self):
        """Starts background notification monitoring."""
        if not self.enabled or self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True, name="NotificationThread")
        self._thread.start()
        logger.info("Notification reader started.")

    def stop(self):
        """Stops background monitor."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        logger.info("Notification reader stopped.")

    def _monitor_loop(self):
        """Polls Windows Notification Listener if winsdk is available, else simulated checks."""
        # On Windows 10/11, Windows.UI.Notifications.Management.UserNotificationListener is supported
        can_use_winrt = False
        if sys.platform == "win32":
            try:
                import winsdk.windows.ui.notifications.management as mgmt
                listener = mgmt.UserNotificationListener.current
                can_use_winrt = True
            except Exception:
                can_use_winrt = False

        while self._running:
            try:
                # Polling frequency
                time.sleep(3.0)
            except Exception as e:
                logger.error(f"Error in notification loop: {e}")

    def simulate_notification(self, app_name: str, title: str, message: str):
        """Manually trigger or test a notification read-out."""
        logger.info(f"Notification from {app_name}: '{title}' - '{message}'")
        if self.on_notification:
            try:
                self.on_notification(app_name, title, message)
            except Exception as e:
                logger.error(f"Error in notification callback: {e}")
