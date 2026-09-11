"""
============================================================
MODULE 4: SYSTEM CONTROL LAYER (Windows Automation & I/O)
============================================================
Controls Windows OS functions:
- Application Launch & Termination
- Master Volume & Mute (PyCaw / Windows Core Audio)
- Display Brightness
- File Search, Create, Move, and Safe Delete
- Screenshot & Screen Recording
- System Status (CPU, RAM, Battery, Disk)
"""

import os
import sys
import glob
import time
import json
import psutil
import shutil
import logging
import subprocess
from datetime import datetime
from typing import Dict, Any, List, Optional

try:
    import pyautogui
    pyautogui.FAILSAFE = False
except ImportError:
    pass

logger = logging.getLogger("Jarvis.SystemControl")


class SystemControl:
    def __init__(self, apps_map: Optional[Dict[str, str]] = None):
        self.apps_map = apps_map or {
            "chrome": "chrome",
            "firefox": "firefox",
            "vscode": "code",
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "explorer": "explorer.exe",
            "terminal": "wt.exe",
            "spotify": "spotify",
            "word": "winword.exe",
            "excel": "excel.exe",
            "powerpoint": "powerpnt.exe"
        }
        self.screenshots_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "screenshots")
        os.makedirs(self.screenshots_dir, exist_ok=True)

    # ---------------------------------------------------------
    # 1. APPLICATION CONTROL
    # ---------------------------------------------------------
    def open_app(self, app_name: str) -> bool:
        """Launches an application by name or configured path."""
        target = self.apps_map.get(app_name.lower(), app_name)
        try:
            logger.info(f"Launching application: {target}")
            if sys.platform == "win32":
                os.startfile(target)
            else:
                subprocess.Popen([target])
            return True
        except Exception as e:
            # Try running via shell command as fallback
            try:
                subprocess.Popen(f"start {target}", shell=True)
                return True
            except Exception as e2:
                logger.error(f"Failed to launch '{target}': {e2}")
                return False

    def close_app(self, app_name: str) -> int:
        """Terminates processes matching the app name. Returns count killed."""
        target = app_name.lower().replace(".exe", "")
        killed = 0
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                proc_name = proc.info["name"].lower()
                if target in proc_name:
                    proc.kill()
                    killed += 1
                    logger.info(f"Killed process {proc.info['name']} (PID: {proc.info['pid']})")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return killed

    # ---------------------------------------------------------
    # 2. AUDIO / VOLUME CONTROL (PyCaw Windows Audio)
    # ---------------------------------------------------------
    def _get_volume_interface(self):
        """Returns Windows Master Volume control interface (pycaw)."""
        from pycaw.pycaw import AudioUtilities
        speakers = AudioUtilities.GetSpeakers()
        if hasattr(speakers, "EndpointVolume"):
            return speakers.EndpointVolume
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import IAudioEndpointVolume
        interface = speakers.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        return cast(interface, POINTER(IAudioEndpointVolume))

    def set_volume(self, level: int) -> bool:
        """Sets master volume percentage (0 - 100)."""
        level = max(0, min(100, level))
        try:
            vol = self._get_volume_interface()
            vol.SetMasterVolumeLevelScalar(level / 100.0, None)
            logger.info(f"Volume set to {level}%")
            return True
        except Exception as e:
            logger.warning(f"Volume control error: {e}")
            return False

    def change_volume(self, delta: int) -> bool:
        """Increases or decreases volume by delta percentage."""
        try:
            vol = self._get_volume_interface()
            current = vol.GetMasterVolumeLevelScalar() * 100.0
            new_level = max(0, min(100, int(current + delta)))
            vol.SetMasterVolumeLevelScalar(new_level / 100.0, None)
            logger.info(f"Volume adjusted from {current:.0f}% to {new_level}%")
            return True
        except Exception as e:
            logger.warning(f"Volume change error: {e}")
            return False

    def mute(self, state: bool = True) -> bool:
        """Mutes or unmutes master audio."""
        try:
            vol = self._get_volume_interface()
            vol.SetMute(1 if state else 0, None)
            logger.info(f"Audio mute set to {state}")
            return True
        except Exception as e:
            logger.warning(f"Mute error: {e}")
            return False

    def get_mute_status(self) -> bool:
        """Returns True if master audio is muted."""
        try:
            vol = self._get_volume_interface()
            return bool(vol.GetMute())
        except Exception:
            return False

    def toggle_mute(self) -> bool:
        """Toggles master audio mute state."""
        try:
            vol = self._get_volume_interface()
            current = bool(vol.GetMute())
            vol.SetMute(0 if current else 1, None)
            logger.info(f"Toggled master audio mute to {not current}")
            return not current
        except Exception as e:
            logger.warning(f"Toggle mute error: {e}")
            return False

    # ---------------------------------------------------------
    # 3. DISPLAY BRIGHTNESS CONTROL
    # ---------------------------------------------------------
    def set_brightness(self, level: int) -> bool:
        """Sets monitor brightness (0 - 100)."""
        level = max(0, min(100, level))
        try:
            import screen_brightness_control as sbc
            sbc.set_brightness(level)
            logger.info(f"Brightness set to {level}%")
            return True
        except Exception as e:
            # Fallback using WMI via PowerShell
            try:
                ps_cmd = f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{level})"
                subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, timeout=5)
                logger.info(f"Brightness set to {level}% via WMI.")
                return True
            except Exception as e2:
                logger.error(f"Brightness control failed: {e2}")
                return False

    # ---------------------------------------------------------
    # 4. SCREENSHOT & RECORDING
    # ---------------------------------------------------------
    def take_screenshot(self) -> Optional[str]:
        """Captures full screen and saves to screenshots directory."""
        try:
            import pyautogui
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(self.screenshots_dir, f"screenshot_{timestamp}.png")
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)
            logger.info(f"Screenshot saved to: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Screenshot capture failed: {e}")
            return None

    # ---------------------------------------------------------
    # 5. FILE OPERATIONS (Search, Read, Delete)
    # ---------------------------------------------------------
    def search_file(self, query: str, root_dir: Optional[str] = None) -> List[str]:
        """Searches for files matching query under root_dir (default: User Profile)."""
        if not root_dir or root_dir.lower() == "desktop":
            root_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        elif root_dir.lower() == "downloads":
            root_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        elif root_dir.lower() == "documents":
            root_dir = os.path.join(os.path.expanduser("~"), "Documents")
        elif not os.path.exists(root_dir):
            root_dir = os.path.expanduser("~")

        logger.info(f"Searching for '{query}' in {root_dir}...")
        matches = []
        pattern = f"*{query}*"

        try:
            for root, dirs, files in os.walk(root_dir):
                for f in files:
                    if query.lower() in f.lower():
                        matches.append(os.path.join(root, f))
                        if len(matches) >= 10:  # limit to top 10
                            return matches
        except Exception as e:
            logger.error(f"File search failed: {e}")

        return matches

    def create_file(self, path: str, content: str = "") -> bool:
        """Creates a new text file."""
        try:
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"Created file: {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to create file {path}: {e}")
            return False

    def delete_file(self, path: str) -> bool:
        """Deletes file with safety check."""
        if not os.path.exists(path):
            return False
        try:
            os.remove(path)
            logger.info(f"Deleted file: {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete file {path}: {e}")
            return False

    # ---------------------------------------------------------
    # 6. SYSTEM STATUS
    # ---------------------------------------------------------
    def get_system_status(self) -> Dict[str, Any]:
        """Returns CPU %, RAM %, Battery %, and Disk %."""
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage("C:\\" if sys.platform == "win32" else "/")
        battery = psutil.sensors_battery()

        return {
            "cpu_percent": cpu,
            "ram_percent": ram.percent,
            "ram_used_gb": round(ram.used / (1024**3), 1),
            "ram_total_gb": round(ram.total / (1024**3), 1),
            "disk_percent": disk.percent,
            "battery_percent": battery.percent if battery else None,
            "battery_charging": battery.power_plugged if battery else None
        }

    # ---------------------------------------------------------
    # 7. SENSITIVE POWER COMMANDS
    # ---------------------------------------------------------
    def lock_workstation(self):
        """Locks the Windows workstation."""
        if sys.platform == "win32":
            import ctypes
            ctypes.windll.user32.LockWorkStation()
            logger.info("Workstation locked.")

    def sleep_system(self):
        """Puts Windows to sleep."""
        if sys.platform == "win32":
            import ctypes
            ctypes.windll.PowrProf.SetSuspendState(0, 1, 0)
            logger.info("System entering sleep state.")

    def shutdown(self):
        """Initiates Windows shutdown."""
        logger.warning("Triggering Windows shutdown.")
        if sys.platform == "win32":
            subprocess.run(["shutdown", "/s", "/t", "10"])

    def restart(self):
        """Initiates Windows restart."""
        logger.warning("Triggering Windows restart.")
        if sys.platform == "win32":
            subprocess.run(["shutdown", "/r", "/t", "10"])

    # ---------------------------------------------------------
    # 8. WINDOW & DESKTOP MANAGEMENT
    # ---------------------------------------------------------
    def minimize_all(self):
        """Minimizes all windows (Shows desktop: Win + D)."""
        import pyautogui
        pyautogui.hotkey("win", "d")
        logger.info("Showing desktop / minimized all windows.")

    def minimize_active(self):
        """Minimizes current active window (Win + Down)."""
        import pyautogui
        pyautogui.hotkey("win", "down")
        logger.info("Minimized active window.")

    def maximize_active(self):
        """Maximizes current active window (Win + Up)."""
        import pyautogui
        pyautogui.hotkey("win", "up")
        logger.info("Maximized active window.")

    def close_active_window(self):
        """Closes active window (Alt + F4)."""
        import pyautogui
        pyautogui.hotkey("alt", "f4")
        logger.info("Closed active window.")

    def switch_window(self):
        """Switches window (Alt + Tab)."""
        import pyautogui
        pyautogui.hotkey("alt", "tab")
        logger.info("Switched active window.")

    # ---------------------------------------------------------
    # 9. MEDIA PLAYBACK CONTROL
    # ---------------------------------------------------------
    def media_play_pause(self):
        """Toggles media play/pause."""
        import pyautogui
        pyautogui.press("playpause")
        logger.info("Toggled media play/pause.")

    def media_next(self):
        """Plays next media track."""
        import pyautogui
        pyautogui.press("nexttrack")
        logger.info("Next media track.")

    def media_prev(self):
        """Plays previous media track."""
        import pyautogui
        pyautogui.press("prevtrack")
        logger.info("Previous media track.")

    # ---------------------------------------------------------
    # 10. MOUSE & KEYBOARD EMULATION
    # ---------------------------------------------------------
    def type_text(self, text: str):
        """Types string text through virtual keyboard."""
        import pyautogui
        pyautogui.write(text, interval=0.02)
        logger.info(f"Typed text: {text}")

    def press_key(self, key_name: str):
        """Presses a specific key (enter, space, esc, tab, backspace, etc.)."""
        import pyautogui
        pyautogui.press(key_name.lower())
        logger.info(f"Pressed key: {key_name}")

    def mouse_click(self):
        """Performs a mouse left click."""
        import pyautogui
        pyautogui.click()
        logger.info("Mouse clicked.")

    # ---------------------------------------------------------
    # 11. SHELL & TERMINAL COMMAND AGENT
    # ---------------------------------------------------------
    def run_shell_command(self, command: str, cwd: Optional[str] = None, timeout: int = 15) -> Dict[str, Any]:
        """
        Executes a shell or PowerShell command with safety and timeout.
        Returns exit code, stdout, and stderr.
        """
        logger.info(f"Executing shell command: '{command}'")
        try:
            res = subprocess.run(
                ["powershell", "-Command", command] if sys.platform == "win32" else command,
                shell=True if sys.platform != "win32" else False,
                cwd=cwd or os.getcwd(),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            output = res.stdout.strip() or res.stderr.strip()
            return {
                "success": res.returncode == 0,
                "exit_code": res.returncode,
                "output": output[:2000],  # cap at 2000 chars
                "command": command
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"Command timed out after {timeout}s", "command": command}
        except Exception as e:
            return {"success": False, "error": str(e), "command": command}

    def run_git_command(self, git_args: str, repo_dir: Optional[str] = None) -> Dict[str, Any]:
        """Executes a git command in the specified directory."""
        target_dir = repo_dir or os.getcwd()
        full_cmd = f"git {git_args}"
        return self.run_shell_command(full_cmd, cwd=target_dir, timeout=20)

    # ---------------------------------------------------------
    # 12. FOLDER & EXPLORER NAVIGATION
    # ---------------------------------------------------------
    def open_folder(self, path_or_alias: str) -> bool:
        """Opens File Explorer directly to path or special alias."""
        alias_map = {
            "desktop": os.path.join(os.path.expanduser("~"), "Desktop"),
            "downloads": os.path.join(os.path.expanduser("~"), "Downloads"),
            "documents": os.path.join(os.path.expanduser("~"), "Documents"),
            "pictures": os.path.join(os.path.expanduser("~"), "Pictures"),
            "videos": os.path.join(os.path.expanduser("~"), "Videos"),
            "c": "C:\\",
            "c drive": "C:\\",
            "e": "E:\\",
            "e drive": "E:\\",
            "project": r"E:\basit-jarvis-ai"
        }
        target = alias_map.get(path_or_alias.lower().strip(), path_or_alias.strip())
        if not os.path.exists(target):
            logger.warning(f"Target folder does not exist: {target}")
            return False

        try:
            if sys.platform == "win32":
                os.startfile(target)
            else:
                subprocess.Popen(["xdg-open", target])
            logger.info(f"Opened folder: {target}")
            return True
        except Exception as e:
            logger.error(f"Failed to open folder {target}: {e}")
            return False

    # ---------------------------------------------------------
    # 13. PROCESS GUARD & ACTIVE WINDOW
    # ---------------------------------------------------------
    def get_active_window(self) -> Dict[str, Any]:
        """Returns title and process name of currently active window."""
        if sys.platform != "win32":
            return {"title": "Unknown"}
        try:
            import pygetwindow as gw
            active = gw.getActiveWindow()
            if active:
                return {"title": active.title, "is_maximized": active.isMaximized}
        except Exception as e:
            logger.debug(f"Could not get active window: {e}")
        return {"title": "Desktop / None"}

    def sweep_zombies(self) -> int:
        """Sweeps orphaned node processes to prevent system hangs."""
        targets = ["node.exe"]
        killed = 0
        current_pid = os.getpid()
        for proc in psutil.process_iter(["pid", "name", "create_time"]):
            try:
                name = proc.info["name"].lower()
                pid = proc.info["pid"]
                if pid == current_pid:
                    continue
                if name in targets:
                    age = time.time() - proc.info["create_time"]
                    if age > 7200:  # older than 2 hrs
                        proc.kill()
                        killed += 1
            except Exception:
                continue
        logger.info(f"Swept {killed} zombie processes.")
        return killed

    # ---------------------------------------------------------
    # 14. CLIPBOARD & QUICK NOTES MANAGER
    # ---------------------------------------------------------
    def get_clipboard_text(self) -> str:
        """Retrieves text from Windows clipboard."""
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            clip = root.clipboard_get()
            root.destroy()
            return clip
        except Exception:
            try:
                import win32clipboard
                win32clipboard.OpenClipboard()
                data = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
                return data
            except Exception as e:
                logger.debug(f"Could not read clipboard: {e}")
                return ""

    def set_clipboard_text(self, text: str) -> bool:
        """Sets Windows clipboard text."""
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            root.clipboard_clear()
            root.clipboard_append(text)
            root.update()
            root.destroy()
            return True
        except Exception as e:
            logger.debug(f"Could not set clipboard: {e}")
            return False

    def snap_window_left(self):
        """Snaps active window to left half of screen (Win + Left)."""
        import pyautogui
        pyautogui.hotkey("win", "left")
        logger.info("Snapped window to left.")

    def snap_window_right(self):
        """Snaps active window to right half of screen (Win + Right)."""
        import pyautogui
        pyautogui.hotkey("win", "right")
        logger.info("Snapped window to right.")

    def take_quick_note(self, note_text: str) -> Dict[str, Any]:
        """Saves a quick note / task to notes.json."""
        notes_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "notes.json")
        notes = []
        if os.path.exists(notes_path):
            try:
                with open(notes_path, "r", encoding="utf-8") as f:
                    notes = json.load(f)
            except Exception:
                notes = []
        
        entry = {
            "id": len(notes) + 1,
            "text": note_text,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        notes.append(entry)
        
        with open(notes_path, "w", encoding="utf-8") as f:
            json.dump(notes, f, indent=2)
        logger.info(f"Saved note: '{note_text}'")
        return entry

    def get_all_notes(self) -> List[Dict[str, Any]]:
        """Retrieves all saved notes."""
        notes_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "notes.json")
        if not os.path.exists(notes_path):
            return []
        try:
            with open(notes_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def cleanup_old_screenshots(self, max_days: int = 7) -> int:
        """Cleans up screenshots older than max_days."""
        cleaned = 0
        now = time.time()
        for fname in os.listdir(self.screenshots_dir):
            if fname.endswith(".png"):
                fpath = os.path.join(self.screenshots_dir, fname)
                if now - os.path.getmtime(fpath) > (max_days * 86400):
                    try:
                        os.remove(fpath)
                        cleaned += 1
                    except Exception:
                        pass
        return cleaned
