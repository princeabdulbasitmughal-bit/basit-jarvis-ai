"""
================================================================================
👑 BASIT JARVIS AI — DROPZONE FILE WATCHER (watchdog + pdf2docx)
================================================================================
Drop any file into E:\\basit-jarvis-ai\\dropzone\\:
  - .pdf  → automatically converted to .docx in dropzone/converted/
  - .docx → automatically converted to .pdf in dropzone/converted/
  - Fires native Windows toast notification + voice alert!

Can be run standalone: python modules/dropzone_watcher.py
Or imported and started as a daemon thread in Jarvis server / voice loop.
================================================================================
"""

import os
import sys
import time
import shutil
import logging
import threading
from pathlib import Path

# Force UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DROPZONE_DIR = os.path.join(BASE_DIR, "dropzone")
CONVERTED_DIR = os.path.join(DROPZONE_DIR, "converted")

os.makedirs(DROPZONE_DIR, exist_ok=True)
os.makedirs(CONVERTED_DIR, exist_ok=True)

logger = logging.getLogger("Jarvis.Dropzone")

def notify(title: str, msg: str):
    """Send modern Windows toast notification."""
    try:
        from win11toast import toast
        toast(title, msg)
    except Exception:
        try:
            from winotify import Notification
            n = Notification(app_id="Basit Jarvis Dropzone", title=title, msg=msg)
            n.show()
        except Exception:
            pass

def speak_alert(text: str):
    """Non-blocking voice alert via pyttsx3."""
    def _speak():
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty('rate', 170)
            engine.say(text)
            engine.runAndWait()
        except Exception:
            pass
    threading.Thread(target=_speak, daemon=True).start()

def process_file(filepath: str):
    """Processes a newly added file in the dropzone."""
    path = Path(filepath)
    if not path.is_file():
        return

    # Skip files inside converted/ or temporary files
    if "converted" in path.parts or path.name.startswith("~") or path.name.startswith("."):
        return

    # Wait a moment for file write completion
    time.sleep(1.0)
    ext = path.suffix.lower()

    if ext == ".pdf":
        out_name = path.stem + ".docx"
        out_path = os.path.join(CONVERTED_DIR, out_name)
        print(f"📄 [DROPZONE] Converting PDF: {path.name} -> {out_name}...")
        try:
            from pdf2docx import Converter
            cv = Converter(str(path))
            cv.convert(out_path, start=0, end=None)
            cv.close()
            print(f"✅ [DROPZONE] Converted: {out_path}")
            notify("Jarvis Dropzone 📄", f"{path.name} converted to Word document!")
            speak_alert(f"Basit bhai, {path.stem} word document ban gaya hai!")
        except Exception as e:
            print(f"❌ [DROPZONE] PDF conversion failed: {e}")
            notify("Jarvis Dropzone Error ❌", f"Could not convert {path.name}: {str(e)[:50]}")

    elif ext in [".docx", ".doc"]:
        out_name = path.stem + ".pdf"
        out_path = os.path.join(CONVERTED_DIR, out_name)
        print(f"📄 [DROPZONE] Converting Word: {path.name} -> {out_name}...")
        converted = False

        # Try LibreOffice
        lo_paths = [
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        ]
        for lo in lo_paths:
            if os.path.exists(lo):
                import subprocess
                subprocess.run(
                    [lo, '--headless', '--convert-to', 'pdf', '--outdir', CONVERTED_DIR, str(path)],
                    capture_output=True, timeout=45
                )
                converted = os.path.exists(out_path)
                break

        # Fallback to win32com if Word is installed
        if not converted:
            try:
                import win32com.client
                word = win32com.client.Dispatch("Word.Application")
                word.Visible = False
                doc = word.Documents.Open(str(path))
                doc.SaveAs(out_path, FileFormat=17)
                doc.Close()
                word.Quit()
                converted = True
            except Exception:
                pass

        if converted and os.path.exists(out_path):
            print(f"✅ [DROPZONE] Converted: {out_path}")
            notify("Jarvis Dropzone 📄", f"{path.name} converted to PDF document!")
            speak_alert(f"Basit bhai, {path.stem} PDF ban gaya hai!")
        else:
            print(f"⚠️ [DROPZONE] Word conversion requires LibreOffice or MS Word.")

class DropzoneHandler:
    def __init__(self):
        from watchdog.events import FileSystemEventHandler
        self.base_class = FileSystemEventHandler

        class _Handler(FileSystemEventHandler):
            def on_created(self, event):
                if not event.is_directory:
                    threading.Thread(target=process_file, args=(event.src_path,), daemon=True).start()

        self.handler = _Handler()

def start_dropzone_watcher(block: bool = False):
    """Starts the dropzone observer."""
    try:
        from watchdog.observers import Observer
        handler_wrapper = DropzoneHandler()
        observer = Observer()
        observer.schedule(handler_wrapper.handler, path=DROPZONE_DIR, recursive=False)
        observer.start()
        print(f"👀 [DROPZONE WATCHER] Monitoring: {DROPZONE_DIR}")
        notify("Jarvis Dropzone Active 👀", f"Drop PDFs or Word docs in dropzone folder for instant conversion!")

        if block:
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                observer.stop()
            observer.join()
        return observer
    except Exception as e:
        print(f"❌ [DROPZONE WATCHER] Failed to start: {e}")
        return None

if __name__ == "__main__":
    print(f"👑 Basit Jarvis Dropzone Watcher starting...")
    start_dropzone_watcher(block=True)
