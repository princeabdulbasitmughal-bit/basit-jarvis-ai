"""
================================================================================
👑 BASIT JARVIS AI — SOVEREIGN MASTER LAUNCHER (Unified Desktop + Tray + Hotkeys)
================================================================================
Single command to launch the full Jarvis OS ecosystem:
  1. Verifies/starts Node.js server (port 8888)
  2. Starts Dropzone Auto-File Watcher (watchdog)
  3. Registers Global Hotkeys (Ctrl+Shift+J, Ctrl+Shift+S, Ctrl+Shift+D)
  4. Launches System Tray Resident Icon (pystray)
  5. Provides interactive Voice / CLI console or silent tray mode

Usage:
  python launch_jarvis_master.py           # Launches full suite with tray & voice
  python launch_jarvis_master.py --tray    # Silent system tray background mode
================================================================================
"""

import os
import sys
import time
import socket
import logging
import subprocess
import threading
import webbrowser

# Force UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DROPZONE_DIR = os.path.join(BASE_DIR, "dropzone")
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
os.makedirs(DROPZONE_DIR, exist_ok=True)
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

logger = logging.getLogger("Jarvis.Master")

def send_toast(title: str, msg: str):
    """Sends native Windows 11 toast notification."""
    def _fire():
        try:
            from win11toast import toast
            toast(title, msg)
        except Exception:
            try:
                from winotify import Notification
                n = Notification(app_id="Basit Jarvis Master", title=title, msg=msg)
                n.show()
            except Exception:
                pass
    threading.Thread(target=_fire, daemon=True).start()

def is_port_open(port: int = 8888) -> bool:
    """Checks if server.js is actively listening on port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(('127.0.0.1', port)) == 0

def ensure_server_running():
    """Starts Node.js server if not already active."""
    if is_port_open(8888):
        print("✅ Jarvis Core Server already running on http://localhost:8888")
        return True

    print("⚡ Starting Jarvis Node.js Server daemon on port 8888...")
    try:
        subprocess.Popen(
            ["node", "server.js"],
            cwd=BASE_DIR,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        # Wait up to 5s for server to bind
        for _ in range(10):
            time.sleep(0.5)
            if is_port_open(8888):
                print("✅ Jarvis Server started successfully on http://localhost:8888")
                return True
    except Exception as e:
        print(f"⚠️ Could not start server: {e}")
    return False

def start_dropzone():
    """Starts dropzone file observer in background."""
    try:
        from modules.dropzone_watcher import start_dropzone_watcher
        obs = start_dropzone_watcher(block=False)
        return obs
    except Exception as e:
        print(f"⚠️ Dropzone watcher error: {e}")
        return None

def trigger_screenshot():
    """Hotkey triggered instant screenshot."""
    ts = time.strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(SCREENSHOTS_DIR, f"hotkey_screenshot_{ts}.png")
    try:
        import pyautogui
        pyautogui.screenshot(out_path)
        send_toast("Screenshot Taken 📸", f"Saved: screenshots/hotkey_screenshot_{ts}.png")
        print(f"📸 Screenshot saved: {out_path}")
    except Exception:
        try:
            from mss import MSS
            with MSS() as sct:
                sct.shot(output=out_path)
                send_toast("Screenshot Taken 📸", f"Saved: {out_path}")
                print(f"📸 Screenshot saved via MSS: {out_path}")
        except Exception as e:
            print(f"⚠️ Screenshot error: {e}")

def register_hotkeys():
    """Registers OS-wide global shortcuts."""
    try:
        import keyboard
        # Ctrl+Shift+S -> Instant Screenshot
        keyboard.add_hotkey("ctrl+shift+s", trigger_screenshot)
        # Ctrl+Shift+D -> Open Dropzone folder
        keyboard.add_hotkey("ctrl+shift+d", lambda: os.startfile(DROPZONE_DIR))
        print("✅ Hotkeys active: [Ctrl+Shift+J] Voice | [Ctrl+Shift+S] Screenshot | [Ctrl+Shift+D] Dropzone")
    except Exception as e:
        print(f"⚠️ Hotkey hook note: {e}")

def start_system_tray():
    """Starts resident tray icon with rich controls."""
    def _run():
        try:
            import pystray
            from PIL import Image, ImageDraw

            # Draw cyan arc reactor icon
            img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw.ellipse([4, 4, 60, 60], outline=(0, 200, 255, 255), width=4)
            draw.ellipse([16, 16, 48, 48], outline=(0, 255, 200, 255), width=3)
            draw.ellipse([26, 26, 38, 38], fill=(0, 255, 255, 255))

            def open_dash(icon, item): webbrowser.open("http://localhost:8888")
            def open_drop(icon, item): os.startfile(DROPZONE_DIR)
            def open_shot(icon, item): os.startfile(SCREENSHOTS_DIR)
            def do_shot(icon, item): trigger_screenshot()
            def do_exit(icon, item):
                icon.stop()
                os._exit(0)

            menu = pystray.Menu(
                pystray.MenuItem("👑 Basit Jarvis AI (Online)", lambda i, it: None, enabled=False),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("🌐 Open Dashboard (Port 8888)", open_dash),
                pystray.MenuItem("📸 Instant Screenshot", do_shot),
                pystray.MenuItem("📂 Open Dropzone Folder", open_drop),
                pystray.MenuItem("📁 Open Screenshots Folder", open_shot),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("❌ Exit Jarvis Suite", do_exit)
            )

            icon = pystray.Icon("BasitJarvis", img, "Basit Jarvis AI", menu)
            icon.run()
        except Exception as e:
            print(f"⚠️ System tray note: {e}")

    threading.Thread(target=_run, daemon=True).start()

def main():
    print("""
╔══════════════════════════════════════════════════════════════════╗
║   👑 BASIT JARVIS AI — SOVEREIGN MASTER LAUNCHER                 ║
║   Full Ecosystem: Web OS + Dropzone + Voice Loop + Global Keys   ║
╚══════════════════════════════════════════════════════════════════╝
""")
    # 1. Start Server
    ensure_server_running()

    # 2. Start Dropzone File Watcher
    start_dropzone()

    # 3. Register Hotkeys
    register_hotkeys()

    # 4. Start System Tray
    start_system_tray()

    # 5. Toast Notification
    send_toast("Basit Jarvis AI 👑", "All systems operational! Press Ctrl+Shift+S for screenshot.")

    # Check mode
    if "--tray" in sys.argv:
        print("\n🟢 Jarvis running in silent background tray mode. Right-click the cyan icon in system tray.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down Jarvis...")
    else:
        # Launch voice or keyboard loop with intelligent hardware auto-detection
        try:
            import jarvis_voice
            from modules.audio_health import get_recommended_interaction_mode
            jarvis_voice.banner()
            jarvis_voice._init_tts()

            mode = get_recommended_interaction_mode()
            if mode == "voice":
                print("\n🎤 Microphone hardware verified! Starting full voice interaction assistant...")
                jarvis_voice._init_stt()
                jarvis_voice.voice_loop()
            else:
                print("\n⌨️ No active microphone detected (or remote session) — starting intelligent keyboard chat mode...")
                jarvis_voice.keyboard_loop()
        except KeyboardInterrupt:
            print("\nShutting down Jarvis...")
        except Exception as e:
            print(f"Voice loop error ({e}), starting keyboard chat mode:")
            import jarvis_voice
            jarvis_voice.keyboard_loop()

if __name__ == "__main__":
    main()
