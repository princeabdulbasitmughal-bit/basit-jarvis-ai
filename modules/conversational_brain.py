"""
================================================================================
👑 BASIT JARVIS AI — CONVERSATIONAL BRAIN (Real Human-Like Interaction)
================================================================================
Yeh module Jarvis ko genuinely human-like banaata hai.
- Natural bilingual conversation (Roman Urdu + English)
- Intent se action tak automatic routing
- Conversational memory (last 10 turns)
- Human-like confirmations: "Ho gaya bhai!" / "Zaroor, abhi karta hoon!"
- Emotional intelligence: boredom, frustration, excitement detect karta hai
"""

import os
import sys
import json
import time
import re
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# ============================================================
# HUMAN PERSONALITY LAYER — Jarvis ki "insaniyat"
# ============================================================

JARVIS_CONFIRMATIONS = {
    "done": [
        "Ho gaya Basit bhai! ✅",
        "Bilkul ho gaya, sir! 🚀",
        "Kaam tamam, boss! 👑",
        "Sorted! Kuch aur chahiye? 😊",
        "Ek second mein kar diya! ✅",
    ],
    "working": [
        "Haan bhai, abhi karta hoon!",
        "Ji bilkul, ek second!",
        "Zaroor, lag gaya kaam!",
        "Abhi karta hoon Basit bhai!",
        "Theek hai bhai, shuru ho gaya! ⚡",
    ],
    "greeting_morning": [
        "Good morning Basit bhai! ☀️ Aaj kya plan hai?",
        "Salam bhai! Subah ki chai ho gayi? Batao kya karna hai aaj!",
        "Morning boss! Fresh start — kya kaam shuru karein?",
    ],
    "greeting_night": [
        "Arre bhai, itni raat ko? Theek ho? 😄 Batao kya chahiye!",
        "Raat ke {hour} baj rahe hain — koi urgent kaam hai?",
        "Late night session! Energy level kaisi hai? Chalo kaam karte hain!",
    ],
    "greeting_day": [
        "Haan bhai, kya haal hai! Batao kya karna hai?",
        "Kya ho raha hai boss! Ready hoon — bol do!",
        "Haan Basit bhai! Aaj kya plan hai?",
    ],
    "boredom": [
        "Arre yaar, chalo kuch naya banate hain! Koi idea hai jo aik arse se dimag mein hai? 🚀",
        "Bore ho rahe ho? Chalte hain coding — koi cool project start karte hain!",
        "Chill time hai — chalo Netflix recommend karun ya kuch naya build karein? 😄",
    ],
    "error": [
        "Yaar thodi problem aa gayi, dekh raha hoon abhi! 🔧",
        "Ek second bhai, kuch fix karna padega — hota hai!",
        "Minor hiccup! Abhi sort karta hoon, tension nahi.",
    ],
    "thanks": [
        "Arre koi baat nahi bhai! Yahi toh mera kaam hai! 😊",
        "Ji ji, hamesha haazir hoon! 👑",
        "Khushi hua bhai! Kuch aur ho toh batao!",
    ],
}

BOREDOM_TRIGGERS = ["bore", "kuch nahi", "neend", "time pass", "kya karo", "tang", "pagal", "ajeeb", "uff", "khali baitha"]
THANKS_TRIGGERS = ["shukriya", "thanks", "thank you", "jazakallah", "great", "shabash", "badhiya", "zabardast", "maza aaya", "bohot khoob", "dhanwad"]
GREETING_TRIGGERS = [
    "salam", "assalam", "hello", "hi ", "hey", "kya ho raha", "kaise ho", "kese ho",
    "kaisa ho", "kesa ho", "kaisa hai", "kesa hai", "kya haal", "kia haal", "kya hal",
    "kia hal", "hal chal", "haal chaal", "aur sunao", "sab theek", "wassup", "what's up",
    "how are you", "how are u", "good morning", "good night", "good evening", "good afternoon",
    "namaste", "adaab"
]

def send_toast_notification(title: str, message: str):
    """Fires native Windows toast notification without blocking."""
    def _fire():
        try:
            from win11toast import toast
            toast(title, message)
        except Exception:
            try:
                from winotify import Notification
                notif = Notification(app_id="Basit Jarvis AI", title=title, msg=message)
                notif.show()
            except Exception:
                pass
    threading.Thread(target=_fire, daemon=True).start()


# ============================================================
# SMART ACTION DETECTOR — Natural language → action
# ============================================================

ACTION_PATTERNS = {
    "whatsapp_send": [
        r"(?P<name>[a-z]+)\s+ko\s+(?:whatsapp|text|msg|message|likho|bol|send)(?:\s+karo|\s+karna|\s+do)?\s+(?P<msg>.+)",
        r"(?:whatsapp|text|send|message)\s+(?P<name>[a-z]+)\s+(?P<msg>.+)",
        r"(?P<name>[a-z]+)\s+ko\s+(?:bol|bolo|keh do|batao)\s+(?P<msg>.+)",
    ],
    "pdf_to_word": [
        r"(?:last|woh|pichli|us)\s+(?:wali\s+)?pdf\s+(?:ko\s+)?(?:word|docx|ms\s+word)\s+(?:mein\s+)?(?:convert|bana|badlo)",
        r"pdf\s+(?:to|ko)\s+word",
        r"(?:convert|change|badlo)\s+(?:pdf\s+to|pdf\s+ko)\s+(?:word|docx)",
    ],
    "word_to_pdf": [
        r"(?:last|woh|pichli)\s+(?:wali\s+)?(?:word|docx)\s+(?:ko\s+)?(?:pdf)\s+(?:mein\s+)?(?:convert|bana)",
        r"(?:word|docx)\s+(?:to|ko)\s+pdf",
    ],
    "summarize_file": [
        r"(?:last|woh|pichli|is)\s+(?:wali\s+)?(?:pdf|file|document)\s+(?:ka\s+)?summary(?:\s+bana|\s+do|\s+batao)?",
        r"(?:summarize|summary\s+karo|khulasa)\s+(?:karo\s+)?(?:is|this)?\s*(?:pdf|file|document)",
    ],
    "screenshot": [
        r"screenshot\s+(?:lo|lao|le\s+lo|karo)",
        r"(?:screen|screen\s+shot)\s+(?:capture|lao|lo)",
    ],
    "open_app": [
        r"(?P<app>chrome|firefox|vs\s*code|vscode|spotify|notepad|excel|word|powerpoint)\s+(?:kholo|open\s+karo|chalao|start\s+karo|launch\s+karo)",
        r"(?:kholo|open\s+karo)\s+(?P<app>chrome|firefox|vs\s*code|vscode|spotify|notepad)",
    ],
    "search_web": [
        r"(?:google|search|dhundo|dhundhao)\s+(?:karo\s+)?(?P<query>.+)",
        r"(?P<query>.+)\s+(?:search\s+karo|google\s+karo|dhundo)",
    ],
    "set_reminder": [
        r"(?:reminder|yaad|yaad\s+dilao|mujhe\s+yaad\s+dilao)\s+(?:karo\s+)?(?P<task>.+)\s+(?:at|baje|ko)\s+(?P<time>\d+(?::\d+)?(?:\s*[ap]m)?)",
        r"(?P<time>\d+(?::\d+)?(?:\s*[ap]m)?)\s+(?:ko|baje|at)\s+(?:mujhe\s+)?(?:remind|yaad\s+dilao)\s+(?P<task>.+)",
    ],
    "play_music": [
        r"(?:music|gaana|song|gana)\s+(?:chala\s+do|chalao|play\s+karo|play|lagao)",
        r"(?:spotify|youtube\s+music)\s+(?:kholo|chalao|open\s+karo)",
        r"(?:chalao|play\s+karo|laga\s+do|lagao)\s+(?P<query>.+?)(?:\s+(?:song|gaana|music))?$",
        r"(?P<query>.+?)\s+(?:chalao|play\s+karo|laga\s+do|sunao)",
    ],
    "set_reminder": [
        r"(?:reminder|alarm|yaad\s+dilao|remind)\s+(?:set\s+karo|lagao|karo)?.*?(?:(\d+)\s*(?:minute|min|second|sec|hour|hr|ghante))?",
        r"(\d+)\s*(?:minute|min|hour|hr|ghante)\s+(?:mein|baad|after)\s+(?P<content>.+)",
        r"(?:remind\s+me|yaad\s+dilana)\s+(?:to\s+|ke\s+)?(?P<content>.+)",
        r"(?:set|lao|lagao)\s+(?:ek\s+)?(?:reminder|alarm)\s+(?:for\s+|ke\s+liye\s+)?(?P<content>.+)",
    ],

    "check_weather": [
        r"(?:weather|mausam)\s+(?:kaisa\s+hai|batao|check\s+karo|kya\s+hai)",
    ],
    "translate": [
        r"(?:translate|tarjuma|urdu\s+mein\s+kaho)\s+(?P<text>.+)",
        r"(?P<text>.+)\s+(?:urdu|english|hindi)\s+mein\s+(?:likho|batao|translate\s+karo)",
    ],
    "calculate": [
        r"(?:calculate|hisab|nikalo|compute)\s+(?P<expr>.+)",
        r"(?P<expr>\d+\s*[\+\-\*\/\^]\s*\d+(?:\s*[\+\-\*\/\^]\s*\d+)*)",
    ],
    "create_note": [
        r"(?:note|naya\s+note|likho)\s+(?:karo\s+)?(?P<content>.+)",
        r"(?:save|sacha\s+karo|store)\s+(?:karo\s+)?(?:yeh|this)?\s*:?\s*(?P<content>.+)",
    ],
    "system_status": [
        r"(?:system|computer|pc|laptop)\s+(?:ki\s+)?(?:status|health|kaisa\s+hai|kya\s+hal\s+hai)",
        r"(?:cpu|ram|disk|battery)\s+(?:kitna|kya\s+hai|check)",
    ],
    "git_commit": [
        r"git\s+commit\s+(?:karo\s+)?(?P<msg>.+)",
        r"(?:commit|save\s+changes|changes\s+save\s+karo)\s+(?:karo\s+)?(?:with\s+)?(?:message\s+)?(?P<msg>.+)",
    ],
    "generate_code": [
        r"(?:code|script|function|api)\s+(?:banao|likho|generate\s+karo)\s+(?:for\s+|ke\s+liye\s+)?(?P<task>.+)",
        r"(?P<task>.+)\s+(?:ka\s+code|ka\s+script|banao|implement\s+karo)",
    ],
    "research_topic": [
        r"(?:research|analyze|pata\s+karo|dhundo)\s+(?:karo\s+)?(?P<topic>.+)",
        r"(?P<topic>.+)\s+(?:ke\s+baray\s+mein|ke\s+baare\s+mein|about)\s+(?:batao|research\s+karo)",
    ],
}


class ConversationalBrain:
    """
    Jarvis ki real human-like conversation engine.
    User kuch bhi bole — yeh samjhega, respond karega, aur khud action lega.
    """

    def __init__(self, ai_brain=None):
        self.ai_brain = ai_brain
        self.conversation_history: List[Dict] = []
        self.max_history = 10
        self._import_counter = 0

        # Load contacts
        self.contacts = self._load_contacts()

        # Last file tracker
        self.last_pdf = None
        self.last_docx = None
        self._scan_recent_files()

    def _load_contacts(self) -> Dict[str, str]:
        contacts = {
            'ali': '923001234567', 'sara': '923211234567',
            'ahmed': '923331234567', 'mama': '923001111111',
            'papa': '923002222222', 'bhai': '923003333333',
            'ammi': '923004444444', 'abu': '923005555555',
            'usman': '923006666666', 'hamza': '923007777777',
            'bilal': '923008888888', 'zara': '923009999999',
            'hira': '923010000000', 'faisal': '923012222222',
        }
        contacts_path = os.path.join(BASE_DIR, 'data', 'contacts.json')
        if os.path.exists(contacts_path):
            try:
                saved = json.loads(open(contacts_path, encoding='utf-8').read())
                contacts.update(saved)
            except Exception:
                pass
        return contacts

    def _scan_recent_files(self):
        """Find the most recent PDF and DOCX files on this machine."""
        try:
            search_dirs = [
                os.path.join(os.path.expanduser("~"), "Desktop"),
                os.path.join(os.path.expanduser("~"), "Downloads"),
                os.path.join(os.path.expanduser("~"), "Documents"),
                os.path.join(BASE_DIR, "reports"),
            ]
            pdfs, docxs = [], []
            for d in search_dirs:
                if not os.path.exists(d): continue
                for f in os.listdir(d):
                    full = os.path.join(d, f)
                    if f.lower().endswith('.pdf'):
                        pdfs.append((os.path.getmtime(full), full))
                    elif f.lower().endswith('.docx'):
                        docxs.append((os.path.getmtime(full), full))
            if pdfs:
                self.last_pdf = sorted(pdfs, reverse=True)[0][1]
            if docxs:
                self.last_docx = sorted(docxs, reverse=True)[0][1]
        except Exception:
            pass

    def _get_greeting_type(self) -> str:
        hour = datetime.now().hour
        if 5 <= hour < 12: return "morning"
        if hour >= 22 or hour < 5: return "night"
        return "day"

    def _pick(self, lst: List[str], extra: Dict = None) -> str:
        import random
        text = random.choice(lst)
        if extra:
            for k, v in extra.items():
                text = text.replace(f"{{{k}}}", str(v))
        return text

    def detect_emotion(self, text: str) -> str:
        """Detect emotional context of user's message."""
        lower = text.lower()
        if any(t in lower for t in BOREDOM_TRIGGERS):
            return "boredom"
        if any(t in lower for t in THANKS_TRIGGERS):
            return "thanks"
        if any(t in lower for t in GREETING_TRIGGERS):
            return "greeting"
        return "neutral"

    def detect_action(self, text: str) -> Optional[Tuple[str, Dict]]:
        """
        Match text against action patterns.
        Returns (action_name, extracted_entities) or None.
        """
        lower = text.lower().strip()
        for action, patterns in ACTION_PATTERNS.items():
            for pat in patterns:
                match = re.search(pat, lower, re.IGNORECASE)
                if match:
                    try:
                        entities = match.groupdict()
                    except Exception:
                        entities = {}
                    return action, entities
        return None

    def execute_action(self, action: str, entities: Dict, original_text: str) -> str:
        """Execute the detected action and return human-like response."""

        if action == "whatsapp_send":
            name = (entities.get("name") or "").strip()
            msg = (entities.get("msg") or "").strip()
            return self._whatsapp_send(name, msg, original_text)

        elif action == "pdf_to_word":
            return self._pdf_to_word()

        elif action == "word_to_pdf":
            return self._word_to_pdf()

        elif action == "summarize_file":
            return self._summarize_last_file()

        elif action == "screenshot":
            return self._take_screenshot()

        elif action == "system_status":
            return self._system_status()

        elif action == "calculate":
            expr = entities.get("expr", "")
            return self._calculate(expr)

        elif action == "check_weather":
            return self._check_weather()

        elif action == "create_note":
            content = entities.get("content", original_text)
            return self._create_note(content)

        elif action == "git_commit":
            msg = entities.get("msg", "Basit bhai ke orders par update")
            return self._git_commit(msg)

        elif action == "open_app":
            app = (entities.get("app") or "").lower().strip()
            return self._open_app(app, original_text)

        elif action == "play_music":
            query = entities.get("query") or entities.get("song") or ""
            return self._play_music(query)

        elif action == "set_reminder":
            content = entities.get("content") or entities.get("task") or original_text
            mins = entities.get("minutes") or entities.get("time") or ""
            return self._set_reminder(content, str(mins))

        elif action == "search_web":
            query = entities.get("query") or original_text
            return self._search_web(query)

        elif action in ("generate_code", "research_topic", "translate"):
            # These go to AI engine routing
            return None

        return None

    # ============================================================
    # ACTION IMPLEMENTATIONS
    # ============================================================

    def _whatsapp_send(self, name: str, msg: str, raw: str) -> str:
        """Send WhatsApp message to contact."""
        import subprocess
        # Clean name
        name = re.sub(r'[^a-z]', '', name.lower()).strip()

        # Find contact
        phone = self.contacts.get(name)
        if not phone:
            # Fuzzy match
            for cn, cp in self.contacts.items():
                if name in cn or cn in name:
                    name = cn; phone = cp; break

        if not phone:
            return (f"Yaar '{name}' contacts mein nahi mila! 😅 "
                    f"Add karne ke liye bolo: 'add contact {name} 923XXXXXXXXX'")

        if not msg:
            # Extract message from raw text more aggressively
            parts = re.split(r'\b(?:karo|karna|bhejo|send|ko|bol|bolo)\b', raw, flags=re.I)
            msg = parts[-1].strip() if len(parts) > 1 else raw

        if not msg:
            wa_url = f"https://web.whatsapp.com/send?phone={phone}"
            subprocess.Popen(f'powershell -Command "Start-Process \'{wa_url}\'"', shell=True)
            return f"{name.capitalize()} ka WhatsApp chat khol diya! 💬 Message type karo."

        # Try whatsapp-web.js node script first, fallback to browser automation
        wa_script = os.path.join(BASE_DIR, 'modules', 'whatsapp_sender.js')
        if os.path.exists(wa_script):
            try:
                result = subprocess.run(
                    ['node', wa_script, phone, msg],
                    capture_output=True, text=True, timeout=30, cwd=BASE_DIR
                )
                if result.returncode == 0 and 'sent' in result.stdout.lower():
                    return (f"{self._pick(JARVIS_CONFIRMATIONS['done'])} "
                            f"{name.capitalize()} ko WhatsApp message bhej diya: \"{msg}\" 📱")
            except Exception:
                pass

        # Fallback: open WhatsApp web with pre-filled message
        encoded_msg = msg.replace(' ', '%20').replace('\n', '%0A')
        wa_url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_msg}"
        subprocess.Popen(f'powershell -Command "Start-Process \'{wa_url}\'"', shell=True)
        return (f"Basit bhai, {name.capitalize()} ka WhatsApp khola hai message ke saath! "
                f"Sirf Enter dabao aur message chala jayega! 📱✅")

    def _pdf_to_word(self) -> str:
        """Convert last PDF to Word document."""
        self._scan_recent_files()

        if not self.last_pdf:
            return "Bhai koi PDF nahi mili downloads ya desktop pe! Pehle koi PDF download karo ya mujhe path bataو."

        try:
            from pdf2docx import Converter
            pdf_path = self.last_pdf
            word_path = pdf_path.replace('.pdf', '.docx').replace('.PDF', '.docx')
            pdf_name = os.path.basename(pdf_path)

            working_msg = f"Ho raha hai bhai! '{pdf_name}' ko Word mein convert kar raha hoon... ⏳"

            cv = Converter(pdf_path)
            cv.convert(word_path, start=0, end=None)
            cv.close()

            self.last_docx = word_path
            word_name = os.path.basename(word_path)
            send_toast_notification("PDF to Word Converted 📄", f"{pdf_name} converted to {word_name}")
            return (f"{self._pick(JARVIS_CONFIRMATIONS['done'])} "
                    f"'{pdf_name}' → '{word_name}' convert ho gaya! "
                    f"File isi folder mein hai: {os.path.dirname(word_path)} 📄✅")


        except ImportError:
            return "Bhai pdf2docx install nahi hai! Ek second: `pip install pdf2docx` run karo."
        except Exception as e:
            return f"Yaar conversion mein thodi problem aa gayi: {str(e)[:100]}. PDF corrupt toh nahi?"

    def _word_to_pdf(self) -> str:
        """Convert last Word file to PDF using LibreOffice or win32com."""
        self._scan_recent_files()
        if not self.last_docx:
            return "Bhai koi Word file nahi mili! Pehle koi .docx file batao ya downloads mein rakh do."

        try:
            import subprocess
            docx_path = self.last_docx
            docx_name = os.path.basename(docx_path)
            out_dir = os.path.dirname(docx_path)

            # Try LibreOffice first
            lo_paths = [
                r"C:\Program Files\LibreOffice\program\soffice.exe",
                r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
            ]
            for lo in lo_paths:
                if os.path.exists(lo):
                    result = subprocess.run(
                        [lo, '--headless', '--convert-to', 'pdf', '--outdir', out_dir, docx_path],
                        capture_output=True, text=True, timeout=30
                    )
                    if result.returncode == 0:
                        pdf_path = docx_path.replace('.docx', '.pdf')
                        return (f"{self._pick(JARVIS_CONFIRMATIONS['done'])} "
                                f"'{docx_name}' → PDF convert ho gaya! 📄✅")

            # Fallback: try win32com (if MS Word is installed)
            try:
                import win32com.client
                word = win32com.client.Dispatch("Word.Application")
                word.Visible = False
                doc = word.Documents.Open(docx_path)
                pdf_path = docx_path.replace('.docx', '.pdf')
                doc.SaveAs(pdf_path, FileFormat=17)
                doc.Close()
                word.Quit()
                return (f"{self._pick(JARVIS_CONFIRMATIONS['done'])} "
                        f"'{docx_name}' → PDF ban gaya via MS Word! 📄✅")
            except Exception:
                pass

            return "Bhai LibreOffice ya MS Word chahiye PDF banane ke liye. LibreOffice install karo (free hai)!"

        except Exception as e:
            return f"Conversion mein masla: {str(e)[:100]}"

    def _summarize_last_file(self) -> str:
        """Summarize the last PDF using AI brain."""
        self._scan_recent_files()
        if not self.last_pdf:
            return "Bhai koi recent PDF nahi mili!"

        try:
            import fitz  # PyMuPDF
            doc = fitz.open(self.last_pdf)
            text = ""
            for page in doc[:5]:  # First 5 pages
                text += page.get_text()
            doc.close()
            text = text[:3000]  # Limit to 3000 chars

            if self.ai_brain:
                prompt = f"Yeh PDF ka content hai. Iska concise summary Roman Urdu mein bana do (200 words max):\n\n{text}"
                summary = self.ai_brain.ask(prompt, task_type="research")
                fname = os.path.basename(self.last_pdf)
                return f"'{fname}' ka summary:\n\n{summary}"
            else:
                return f"PDF text (pehle 500 chars):\n{text[:500]}..."

        except Exception as e:
            return f"Summary mein masla: {str(e)[:100]}"

    def _take_screenshot(self) -> str:
        """Take a screenshot and save it."""
        try:
            import subprocess
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            out_dir = os.path.join(BASE_DIR, "screenshots")
            os.makedirs(out_dir, exist_ok=True)
            out_path = os.path.join(out_dir, f"screenshot_{ts}.png")

            # 1. Try pyautogui
            try:
                import pyautogui
                pyautogui.screenshot(out_path)
                send_toast_notification("Screenshot Captured 📸", f"Saved: screenshots/screenshot_{ts}.png")
                return f"{self._pick(JARVIS_CONFIRMATIONS['done'])} Screenshot le liya! 📸 Saved: screenshots/screenshot_{ts}.png"
            except Exception:
                pass

            # 2. Try mss
            try:
                from mss import MSS
                with MSS() as sct:
                    sct.shot(output=out_path)
                    send_toast_notification("Screenshot Captured 📸", f"Saved: screenshots/screenshot_{ts}.png")
                    return f"{self._pick(JARVIS_CONFIRMATIONS['done'])} Screenshot le liya via MSS! 📸 Saved: screenshots/screenshot_{ts}.png"
            except Exception:
                pass

            # 3. Try PowerShell
            try:
                ps_file = os.path.join(out_dir, "_grab.ps1")
                with open(ps_file, "w", encoding="utf-8") as f:
                    f.write(f'''
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$b = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bmp = New-Object System.Drawing.Bitmap($b.Width, $b.Height)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($b.Location, [System.Drawing.Point]::Empty, $b.Size)
$bmp.Save("{out_path.replace(os.sep, '/')}")
$g.Dispose()
$bmp.Dispose()
''')
                subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', ps_file], capture_output=True, timeout=10)
                if os.path.exists(out_path):
                    send_toast_notification("Screenshot Captured 📸", f"Saved: screenshots/screenshot_{ts}.png")
                    return f"Screenshot le liya! 📸 Saved: screenshots/screenshot_{ts}.png"
            except Exception:
                pass

            return "Bhai screen abhi locked ya remote session mein hai, is liye screenshot nahi ban saka. Jab display active ho tab dobara bolo! 📸"

        except Exception as e:
            return f"Screenshot mein masla: {str(e)[:80]}"


    def _system_status(self) -> str:
        """Get system health status."""
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=0.5)
            ram = psutil.virtual_memory()
            disk = psutil.disk_usage('C:\\')

            status_emoji = "🟢" if cpu < 60 else "🟡" if cpu < 85 else "🔴"
            ram_used_gb = round(ram.used / (1024**3), 1)
            ram_total_gb = round(ram.total / (1024**3), 1)
            disk_free_gb = round(disk.free / (1024**3), 1)

            return (
                f"{status_emoji} System Status:\n"
                f"• CPU: {cpu}%\n"
                f"• RAM: {ram_used_gb}GB / {ram_total_gb}GB ({ram.percent}%)\n"
                f"• Disk (C:): {disk_free_gb}GB free\n"
                f"• {'System theek hai, tension nahi! 😊' if cpu < 80 else 'CPU thoda busy hai bhai!'}"
            )
        except Exception:
            return "System status check nahi ho saka. psutil install hai?"

    def _calculate(self, expr: str) -> str:
        """Safely evaluate math expression."""
        try:
            expr_clean = re.sub(r'[^0-9\+\-\*\/\.\(\)\s\^]', '', expr)
            expr_clean = expr_clean.replace('^', '**')
            result = eval(expr_clean, {"__builtins__": {}}, {})
            return f"Hisab: {expr_clean} = **{result}** ✅"
        except Exception:
            return f"Bhai yeh expression samajh nahi aaya: '{expr}'. Seedha likho jaise '25 * 4 + 10'."

    def _check_weather(self) -> str:
        """Check weather using wttr.in."""
        try:
            import urllib.request
            with urllib.request.urlopen("https://wttr.in/?format=3&lang=ur", timeout=3) as r:
                weather = r.read().decode('utf-8', errors='ignore').strip()
            return f"Mausam: {weather} 🌤️"
        except Exception:
            return "Bhai weather API reach nahi ho raha, internet check karo!"

    def _create_note(self, content: str) -> str:
        """Save a quick note."""
        try:
            notes_path = os.path.join(BASE_DIR, 'notes.json')
            notes = []
            if os.path.exists(notes_path):
                try:
                    notes = json.loads(open(notes_path).read())
                    if not isinstance(notes, list): notes = []
                except Exception:
                    notes = []
            note = {
                "id": len(notes) + 1,
                "content": content,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "created_by": "voice"
            }
            notes.append(note)
            with open(notes_path, 'w', encoding='utf-8') as f:
                json.dump(notes, f, indent=2, ensure_ascii=False)
            return f"{self._pick(JARVIS_CONFIRMATIONS['done'])} Note save ho gaya: \"{content[:60]}{'...' if len(content) > 60 else ''}\" 📝"
        except Exception as e:
            return f"Note save nahi ho saka: {str(e)[:80]}"

    def _git_commit(self, msg: str) -> str:
        """Auto git add + commit."""
        import subprocess
        try:
            subprocess.run(['git', 'add', '-A'], cwd=BASE_DIR, capture_output=True, timeout=5)
            result = subprocess.run(
                ['git', 'commit', '-m', msg],
                cwd=BASE_DIR, capture_output=True, text=True, timeout=10
            )
            if 'nothing to commit' in result.stdout or 'nothing to commit' in result.stderr:
                return "Bhai koi naya change nahi hai commit karne ke liye! Sab already saved hai. 👍"
            if result.returncode == 0:
                return f"{self._pick(JARVIS_CONFIRMATIONS['done'])} Git commit ho gaya: \"{msg}\" 🌳✅"
            return f"Commit mein kuch issue: {result.stderr[:100]}"
        except Exception as e:
            return f"Git commit nahi ho saka: {str(e)[:80]}"


    def _open_app(self, app: str, raw: str) -> str:
        """Open an application by name."""
        import subprocess
        APP_MAP = {
            'chrome': 'start chrome',
            'browser': 'start chrome',
            'google': 'start chrome',
            'vscode': 'code',
            'vs code': 'code',
            'code': 'code',
            'notepad': 'notepad',
            'calculator': 'calc',
            'calc': 'calc',
            'spotify': 'start spotify:',
            'whatsapp': 'start https://web.whatsapp.com',
            'youtube': 'start https://youtube.com',
            'telegram': 'start https://web.telegram.org',
            'gmail': 'start https://mail.google.com',
            'explorer': 'explorer',
            'file manager': 'explorer',
            'task manager': 'taskmgr',
            'word': 'start winword',
            'excel': 'start excel',
            'powerpoint': 'start powerpnt',
        }
        # Find best match
        cmd = None
        for key, val in APP_MAP.items():
            if key in app or key in raw.lower():
                cmd = val
                app = key
                break
        if not cmd:
            # Try to extract app name from raw text
            m = re.search(r'(?:kholo|open|launch|start|chalo)\s+(\w+)', raw, re.I)
            if m:
                guessed = m.group(1).lower()
                cmd = f'start {guessed}'
                app = guessed
        if cmd:
            try:
                subprocess.Popen(cmd, shell=True)
                return f"{self._pick(JARVIS_CONFIRMATIONS['done'])} {app.title()} khol diya hai! 🚀"
            except Exception as e:
                return f"{app.title()} nahi khul saka: {str(e)[:60]}"
        return f"Kaunsi app kholni hai bhai? Naam batao! 🤔"

    def _play_music(self, query: str) -> str:
        """Open Spotify or YouTube Music with a song/playlist."""
        import subprocess, urllib.parse
        try:
            if query:
                yt_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
                subprocess.Popen(f'start "" "{yt_url}"', shell=True)
                return f"YouTube par \"{query}\" search kar diya — ab maza karo! 🎵"
            else:
                subprocess.Popen('start spotify:', shell=True)
                return "Spotify khol diya hai Basit bhai! 🎶"
        except Exception as e:
            return f"Music player nahi khul saka: {str(e)[:60]}"

    def _set_reminder(self, content: str, time_str: str) -> str:
        """Set a reminder — saves to reminders.json and fires background alert."""
        import threading
        reminders_path = os.path.join(BASE_DIR, 'data', 'reminders.json')
        os.makedirs(os.path.join(BASE_DIR, 'data'), exist_ok=True)
        # Parse time
        delay_sec = 300  # default 5 min
        m = re.search(r'(\d+)\s*(minute|min|second|sec|ghante|hour|hr)', time_str + ' ' + content, re.I)
        if m:
            val = int(m.group(1))
            unit = m.group(2).lower()
            if unit.startswith('sec'):
                delay_sec = val
            elif unit.startswith('hour') or unit.startswith('ghant') or unit.startswith('hr'):
                delay_sec = val * 3600
            else:
                delay_sec = val * 60
        try:
            reminders = []
            if os.path.exists(reminders_path):
                with open(reminders_path, encoding='utf-8') as f:
                    reminders = json.load(f)
            reminder = {
                "id": len(reminders) + 1,
                "task": content[:100],
                "delay_sec": delay_sec,
                "set_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "fire_at": (datetime.now() + timedelta(seconds=delay_sec)).strftime("%Y-%m-%d %H:%M:%S")
            }
            reminders.append(reminder)
            with open(reminders_path, 'w', encoding='utf-8') as f:
                json.dump(reminders, f, indent=2, ensure_ascii=False)
            # Fire alert in background thread
            def _alert():
                time.sleep(delay_sec)
                print(f"\n🔔 JARVIS REMINDER: {content}\n")
                send_toast_notification("Jarvis Reminder 🔔", f"Basit bhai! {content}")
            threading.Thread(target=_alert, daemon=True).start()
            mins = delay_sec // 60
            secs = delay_sec % 60
            time_msg = f"{mins} minute" if mins else f"{secs} second"
            send_toast_notification("Reminder Set ⏰", f"{time_msg} baad: {content[:40]}")
            return f"⏰ Reminder set! {time_msg} baad main aapko yaad dilaunga: \"{content[:50]}\" 🔔"

        except Exception as e:
            return f"Reminder nahi lag saka: {str(e)[:60]}"

    def _search_web(self, query: str) -> str:
        """Open Google search for a query."""
        import subprocess, urllib.parse
        try:
            url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
            subprocess.Popen(f'start "" "{url}"', shell=True)
            return f"Google par \"{query}\" search kar diya! 🔍"
        except Exception as e:
            return f"Search nahi ho saka: {str(e)[:60]}"

    # ============================================================
    # MAIN CONVERSATION HANDLER
    # ============================================================

    def respond(self, user_input: str) -> Dict[str, Any]:
        """
        Main entry point. Returns:
        {
            "response": str,  # Human-like text response
            "action_taken": str,  # What action was executed

            "action_result": str,  # Result of action
            "needs_engine": str,  # If should route to basit1/2/3 etc.
            "speak": str,  # What Jarvis should say (short, voice-friendly)
        }
        """
        text = user_input.strip()
        if not text:
            return {"response": "Haan bhai, bol do!", "speak": "Haan bhai?", "action_taken": None}

        # Add to history
        self.conversation_history.append({"role": "user", "content": text, "time": datetime.now().isoformat()})
        if len(self.conversation_history) > self.max_history * 2:
            self.conversation_history = self.conversation_history[-self.max_history * 2:]

        lower = text.lower()

        # 1. EMOTIONAL CONTEXT
        emotion = self.detect_emotion(text)
        if emotion == "boredom":
            reply = self._pick(JARVIS_CONFIRMATIONS["boredom"])
            return {"response": reply, "speak": reply, "action_taken": "conversation", "needs_engine": None}

        if emotion == "thanks":
            reply = self._pick(JARVIS_CONFIRMATIONS["thanks"])
            return {"response": reply, "speak": reply, "action_taken": "conversation", "needs_engine": None}

        if emotion == "greeting":
            hour = datetime.now().hour
            gtype = self._get_greeting_type()
            if gtype == "morning":
                reply = self._pick(JARVIS_CONFIRMATIONS["greeting_morning"])
            elif gtype == "night":
                reply = self._pick(JARVIS_CONFIRMATIONS["greeting_night"], {"hour": hour})
            else:
                reply = self._pick(JARVIS_CONFIRMATIONS["greeting_day"])
            return {"response": reply, "speak": reply, "action_taken": "conversation", "needs_engine": None}

        # 2. ACTION DETECTION
        detected = self.detect_action(text)
        if detected:
            action_name, entities = detected
            working_reply = self._pick(JARVIS_CONFIRMATIONS["working"])

            # Execute
            result = self.execute_action(action_name, entities, text)

            if result:
                # Action completed — update history
                self.conversation_history.append({"role": "jarvis", "content": result, "time": datetime.now().isoformat()})
                # Make a short voice-friendly version
                speak = result.split('\n')[0][:100]
                return {
                    "response": result,
                    "speak": speak,
                    "action_taken": action_name,
                    "action_result": result,
                    "needs_engine": None
                }
            else:
                # Action needs engine (code gen, research, etc.)
                engine_map = {
                    "generate_code": "basit1",
                    "research_topic": "basit2",
                    "translate": None,
                    "search_web": None,
                }
                engine = engine_map.get(action_name)
                return {
                    "response": working_reply,
                    "speak": working_reply,
                    "action_taken": action_name,
                    "needs_engine": engine
                }

        # 3. ENGINE ROUTING HINTS
        if re.search(r'\b(?:code|script|api|function|program|app|build|implement|develop)\b', lower):
            return {
                "response": self._pick(JARVIS_CONFIRMATIONS["working"]),
                "speak": "Ji bhai, code likh raha hoon!",
                "action_taken": "route_to_engine",
                "needs_engine": "basit1"
            }

        if re.search(r'\b(?:research|analyze|explain|kya hai|batao|compare|difference|pata karo)\b', lower):
            return {
                "response": self._pick(JARVIS_CONFIRMATIONS["working"]),
                "speak": "Ji bhai, research kar raha hoon!",
                "action_taken": "route_to_engine",
                "needs_engine": "basit2"
            }

        if re.search(r'\b(?:security|audit|hack|vulnerability|scan)\b', lower):
            return {
                "response": "Security check shuru kar raha hoon! 🛡️",
                "speak": "Security audit shuru ho gaya!",
                "action_taken": "route_to_engine",
                "needs_engine": "basit3"
            }

        if re.search(r'\b(?:stock|market|invest|nvda|btc|tsla|aapl|crypto|price|trading)\b', lower):
            return {
                "response": "Market analysis kar raha hoon! 📈",
                "speak": "Market analysis shuru ho gaya Basit bhai!",
                "action_taken": "route_to_engine",
                "needs_engine": "basit4"
            }

        # 4. GENERAL AI CONVERSATION
        return {
            "response": None,  # Let AI brain handle
            "speak": None,
            "action_taken": "ai_conversation",
            "needs_engine": None
        }

    def get_history_for_ai(self) -> List[Dict]:
        """Format conversation history for AI brain."""
        formatted = []
        for turn in self.conversation_history[-6:]:
            formatted.append({
                "role": "user" if turn["role"] == "user" else "assistant",
                "content": turn["content"]
            })
        return formatted


# ============================================================
# SINGLETON — server.js can import once and reuse
# ============================================================
_brain_instance = None

def get_brain():
    global _brain_instance
    if _brain_instance is None:
        _brain_instance = ConversationalBrain()
    return _brain_instance


if __name__ == "__main__":
    # Quick test
    brain = ConversationalBrain()
    test_inputs = [
        "Ali ko WhatsApp karo kal meeting 5 baje hai",
        "Last wali PDF ko Word mein convert kar do",
        "System ka status batao",
        "Bore ho raha hoon yaar",
        "Shukriya bhai bahut help ki",
        "100 * 25 + 500 calculate karo",
        "Screenshot lo",
    ]
    for inp in test_inputs:
        print(f"\n>>> USER: {inp}")
        result = brain.respond(inp)
        print(f"JARVIS: {result['response']}")
        if result.get('needs_engine'):
            print(f"[ROUTES TO]: {result['needs_engine']}")
