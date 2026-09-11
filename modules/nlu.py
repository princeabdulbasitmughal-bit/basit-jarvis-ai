"""
================================================================================
👑 BASIT JARVIS AI — BILINGUAL NLU & INTENT PARSER (English + Roman Urdu + Urdu)
================================================================================
Parses voice and text commands into structured intent objects:
- Full English & Roman Urdu natural language understanding
- Native Slash Commands: /basit1, /basit2, /basit3, /basitloop
- Compound commands ('open chrome and set volume to 80')
- OS, Terminal, Git, Apps, Audio, Media, Brightness, Folders, & AI Routing
"""

import re
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("Jarvis.NLU")


class NaturalLanguageUnderstanding:
    def __init__(self, app_aliases: Optional[Dict[str, str]] = None):
        self.app_aliases = app_aliases or {
            "chrome": "chrome",
            "google chrome": "chrome",
            "browser": "chrome",
            "firefox": "firefox",
            "vs code": "vscode",
            "vscode": "vscode",
            "code": "vscode",
            "visual studio code": "vscode",
            "notepad": "notepad",
            "editor": "notepad",
            "calculator": "calculator",
            "calc": "calculator",
            "spotify": "spotify",
            "music": "spotify",
            "terminal": "terminal",
            "cmd": "terminal",
            "powershell": "terminal",
            "command prompt": "terminal",
            "explorer": "explorer",
            "files": "explorer",
            "file explorer": "explorer",
            "word": "word",
            "ms word": "word",
            "excel": "excel",
            "powerpoint": "powerpoint",
            "ppt": "powerpoint"
        }

    def parse(self, text: str) -> List[Dict[str, Any]]:
        """
        Parses text into a list of executable intent objects.
        Handles compound commands connected by 'and', 'then', 'aur', 'phir', comma.
        """
        text = text.strip()
        if not text:
            return []

        logger.debug(f"Parsing user utterance: '{text}'")

        # Split compound commands
        sub_commands = self._split_compound_commands(text)
        intents = []

        for cmd in sub_commands:
            intent = self._parse_single_command(cmd)
            if intent:
                intents.append(intent)

        # Fallback if nothing matched: route to AI Brain
        if not intents and text:
            intents.append({
                "intent": "ai_query",
                "entities": {"query": text},
                "raw": text
            })

        return intents

    def _split_compound_commands(self, text: str) -> List[str]:
        """Splits commands connected by 'and then', 'then', 'and', 'aur phir', 'phir', 'aur', or commas."""
        # Avoid splitting if it's a slash command payload
        if text.startswith(("/basit", "basit 1", "basit 2", "basit 3", "basit loop")):
            return [text]

        pattern = r"\b(?:and\s+then|then|and|aur\s+phir|phir|aur)\b|,"
        chunks = re.split(pattern, text, flags=re.IGNORECASE)
        cleaned = [c.strip() for c in chunks if c.strip()]
        return cleaned if cleaned else [text]

    def _parse_single_command(self, cmd: str) -> Optional[Dict[str, Any]]:
        lower = cmd.lower().strip()

        # ======================================================================
        # 1. BASIT SLASH COMMANDS (/basit1, /basit2, /basit3, /basitloop)
        # ======================================================================
        # /basit1: Ultra-Fast Coding
        basit1_match = re.search(r"^(?:/basit1|basit\s*(?:1|one)|code\s+generator|generate\s+code|code\s+karo)\s*(.*)$", lower)
        if basit1_match:
            payload = basit1_match.group(1).strip() or cmd
            return {
                "intent": "basit1_code",
                "entities": {"prompt": payload},
                "raw": cmd
            }

        # /basit2: Deep Research
        basit2_match = re.search(r"^(?:/basit2|basit\s*(?:2|two)|deep\s+research|research\s+karo|research)\s*(.*)$", lower)
        if basit2_match:
            payload = basit2_match.group(1).strip() or cmd
            return {
                "intent": "basit2_research",
                "entities": {"query": payload},
                "raw": cmd
            }

        # /basit3: Security Audit & Process Guard
        basit3_match = re.search(r"^(?:/basit3|basit\s*(?:3|three)|security\s+audit|security\s+check|clean\s+processes|sweep\s+zombies|zombie\s+sweeper|process\s+guard)\s*(.*)$", lower)
        if basit3_match:
            action = basit3_match.group(1).strip() or "all"
            return {
                "intent": "basit3_guardian",
                "entities": {"action": action},
                "raw": cmd
            }

        # /basitloop: Continuous Autonomous Loop
        loop_match = re.search(r"^(?:/basitloop|basit\s*loop|start\s*loop|loop\s*chalao|autonomous\s*mode|autonomous\s*build)\s*(.*)$", lower)
        if loop_match:
            goal = loop_match.group(1).strip() or "audit and optimize workspace"
            return {
                "intent": "basit_loop",
                "entities": {"goal": goal},
                "raw": cmd
            }

        # ======================================================================
        # 2. MACROS (e.g., 'start coding mode', 'activate work mode', 'coding mode')
        # ======================================================================
        macro_match = re.search(r"\b(?:start|activate|run|enter)?\s*([a-z0-9_\s]+?\s+mode)\b", lower)
        if macro_match:
            mode_name = macro_match.group(1).strip()
            return {
                "intent": "run_macro",
                "entities": {"macro_name": mode_name},
                "raw": cmd
            }

        # ======================================================================
        # 3. TERMINAL & GIT COMMANDS
        # ======================================================================
        git_match = re.search(r"\bgit\s+(status|pull|push|commit|diff|log|add|checkout|branch)(.*)$", lower)
        if git_match:
            git_args = git_match.group(1) + (git_match.group(2) or "")
            return {
                "intent": "run_git_command",
                "entities": {"args": git_args.strip()},
                "raw": cmd
            }

        shell_match = re.search(r"\b(?:run|execute|chalao)\s+(?:in\s+)?(?:terminal|powershell|cmd|shell):\s*(.+)$", lower)
        if not shell_match:
            shell_match = re.search(r"\b(?:terminal|powershell|cmd)\s+(?:mein|me)\s+(?:run\s+karo|chalao|execute\s+karo)\s*(.+)$", lower)
        if shell_match:
            return {
                "intent": "run_terminal_command",
                "entities": {"command": shell_match.group(1).strip()},
                "raw": cmd
            }

        # ======================================================================
        # 4. FOLDER & EXPLORER (Urdu & English)
        # ======================================================================
        folder_match = re.search(r"\b(?:open\s+folder|folder\s+kholo|open\s+directory)\s+([a-z0-9_\-\s]+)$", lower)
        if not folder_match:
            folder_match = re.search(r"\b([a-z0-9_\-]+(?:\s+drive)?)\s+(?:folder\s+)?(?:kholo|open\s+karo)$", lower)
            if folder_match and folder_match.group(1).strip() in ["desktop", "downloads", "documents", "pictures", "videos", "c drive", "e drive", "c", "e"]:
                return {
                    "intent": "open_folder",
                    "entities": {"folder": folder_match.group(1).strip()},
                    "raw": cmd
                }
        if folder_match:
            target_folder = folder_match.group(1).strip()
            if target_folder in ["desktop", "downloads", "documents", "pictures", "videos", "c drive", "e drive", "c", "e", "project"]:
                return {
                    "intent": "open_folder",
                    "entities": {"folder": target_folder},
                    "raw": cmd
                }

        # ======================================================================
        # 5. OPEN / CLOSE APP (Urdu & English)
        # ======================================================================
        # Urdu: 'chrome kholo', 'vs code open karo', 'spotify chalao'
        urdu_open = re.search(r"\b([a-z0-9_\s]+?)\s+(?:kholo|open\s+karo|chalao|start\s+karo)$", lower)
        if urdu_open:
            potential_app = urdu_open.group(1).strip()
            matched_app = self._resolve_app(potential_app)
            if matched_app:
                return {
                    "intent": "open_app",
                    "entities": {"app": matched_app, "target": potential_app},
                    "raw": cmd
                }

        # English: 'open chrome', 'launch vs code', 'start spotify'
        open_match = re.search(r"\b(?:open|launch|start|run)\s+([a-z0-9_\s]+)$", lower)
        if open_match:
            target = open_match.group(1).strip()
            matched_app = self._resolve_app(target)
            if matched_app:
                return {
                    "intent": "open_app",
                    "entities": {"app": matched_app, "target": target},
                    "raw": cmd
                }
            elif target.startswith("http") or "." in target:
                return {
                    "intent": "open_url",
                    "entities": {"url": target},
                    "raw": cmd
                }

        # Urdu: 'chrome band karo', 'spotify close karo'
        urdu_close = re.search(r"\b([a-z0-9_\s]+?)\s+(?:band\s+karo|close\s+karo|kill\s+karo|hatao)$", lower)
        if urdu_close:
            potential_app = urdu_close.group(1).strip()
            matched_app = self._resolve_app(potential_app)
            if matched_app:
                return {
                    "intent": "close_app",
                    "entities": {"app": matched_app},
                    "raw": cmd
                }

        # English: 'close chrome', 'exit spotify', 'kill notepad'
        close_match = re.search(r"\b(?:close|quit|exit|kill|terminate)\s+([a-z0-9_\s]+)$", lower)
        if close_match:
            target = close_match.group(1).strip()
            matched_app = self._resolve_app(target)
            return {
                "intent": "close_app",
                "entities": {"app": matched_app or target},
                "raw": cmd
            }

        # ======================================================================
        # 6. FILE SEARCH
        # ======================================================================
        file_search = re.search(r"\b(?:search|find)\s+file\s+([a-z0-9_\-\.]+)(?:\s+(?:in|on)\s+([a-z0-9_\-\.\s]+))?", lower)
        if not file_search:
            file_search = re.search(r"\bfile\s+([a-z0-9_\-\.]+)\s+(?:dhoondo|search\s+karo)", lower)
            if file_search:
                return {
                    "intent": "search_file",
                    "entities": {"filename": file_search.group(1).strip(), "location": "desktop"},
                    "raw": cmd
                }
        if file_search:
            return {
                "intent": "search_file",
                "entities": {
                    "filename": file_search.group(1).strip(),
                    "location": file_search.group(2).strip() if file_search.group(2) else "desktop"
                },
                "raw": cmd
            }

        # ======================================================================
        # 7. WEB SEARCH (Urdu & English)
        # ======================================================================
        # Urdu: 'google per cats search karo', 'youtube per python chalao'
        urdu_search = re.search(r"\b(google|youtube|bing|github)\s+p(?:e|er)\s+(.+?)\s+(?:search\s+karo|dhoondo|lagao|chalao)$", lower)
        if urdu_search:
            return {
                "intent": "web_search",
                "entities": {"query": urdu_search.group(2).strip(), "engine": urdu_search.group(1)},
                "raw": cmd
            }

        # English: 'search cats on google', 'search for latest ai news'
        search_match = re.search(r"\b(?:search(?:\s+for)?|google|look\s+up)\s+(.+?)(?:\s+on\s+(google|youtube|bing|github))?$", lower)
        if search_match:
            query = search_match.group(1).strip()
            engine = search_match.group(2) or "google"
            return {
                "intent": "web_search",
                "entities": {"query": query, "engine": engine},
                "raw": cmd
            }

        # ======================================================================
        # 8. VOLUME & SPEAKER CONTROL (Urdu & English)
        # ======================================================================
        if any(w in lower for w in [
            "speaker band", "speaker off", "speaker mute", "bolna band", "chup ho jao", 
            "voice mute", "voice off", "mute voice", "mute speaker", "stop speaking"
        ]):
            return {"intent": "toggle_speaker", "entities": {"state": "off"}, "raw": cmd}

        if any(w in lower for w in [
            "speaker on", "speaker kholo", "speaker chalao", "speaker unmute", 
            "voice on", "voice unmute", "unmute voice", "unmute speaker", "start speaking"
        ]):
            return {"intent": "toggle_speaker", "entities": {"state": "on"}, "raw": cmd}

        if "toggle speaker" in lower or "speaker toggle" in lower or "voice toggle" in lower:
            return {"intent": "toggle_speaker", "entities": {"state": "toggle"}, "raw": cmd}

        if "mute" in lower or "awaz band" in lower or "aawaz band" in lower:
            return {"intent": "set_volume", "entities": {"action": "mute"}, "raw": cmd}
        if "unmute" in lower or "awaz kholo" in lower or "aawaz kholo" in lower:
            return {"intent": "set_volume", "entities": {"action": "unmute"}, "raw": cmd}

        vol_val = re.search(r"\b(?:set\s+)?volume\s+(?:to\s+)?(\d{1,3})%?", lower)
        if not vol_val:
            vol_val = re.search(r"\b(?:awaz|volume)\s+(\d{1,3})\s*(?:%|percent|kardo|karo)?", lower)
        if vol_val:
            val = max(0, min(100, int(vol_val.group(1))))
            return {"intent": "set_volume", "entities": {"value": val}, "raw": cmd}

        if any(w in lower for w in ["volume up", "increase volume", "awaz barhao", "aawaz tez", "volume barha"]):
            return {"intent": "change_volume", "entities": {"delta": 15}, "raw": cmd}
        if any(w in lower for w in ["volume down", "decrease volume", "lower volume", "awaz kam", "aawaz kam", "volume ghatao"]):
            return {"intent": "change_volume", "entities": {"delta": -15}, "raw": cmd}

        # ======================================================================
        # 9. BRIGHTNESS (Urdu & English)
        # ======================================================================
        bright_val = re.search(r"\b(?:set\s+)?brightness\s+(?:to\s+)?(\d{1,3})%?", lower)
        if not bright_val:
            bright_val = re.search(r"\b(?:roshni|brightness)\s+(\d{1,3})\s*(?:%|percent|kardo|karo)?", lower)
        if bright_val:
            val = max(0, min(100, int(bright_val.group(1))))
            return {"intent": "set_brightness", "entities": {"value": val}, "raw": cmd}

        # ======================================================================
        # 10. SCREENSHOT (Urdu & English)
        # ======================================================================
        if any(w in lower for w in ["screenshot", "screen capture", "screen ki photo", "screen shot"]):
            return {"intent": "take_screenshot", "entities": {}, "raw": cmd}

        # ======================================================================
        # 11. WINDOW & DESKTOP MANAGEMENT
        # ======================================================================
        if any(w in lower for w in ["show desktop", "minimize all", "desktop view", "desktop dikhao", "saari windows minimize"]):
            return {"intent": "minimize_all", "entities": {}, "raw": cmd}
        if "snap left" in lower or "window left" in lower or "baayein kardo" in lower:
            return {"intent": "snap_window_left", "entities": {}, "raw": cmd}
        if "snap right" in lower or "window right" in lower or "daayein kardo" in lower:
            return {"intent": "snap_window_right", "entities": {}, "raw": cmd}
        if "minimize" in lower or "chhota kardo" in lower:
            return {"intent": "minimize_active", "entities": {}, "raw": cmd}
        if "maximize" in lower or "bada kardo" in lower:
            return {"intent": "maximize_active", "entities": {}, "raw": cmd}
        if "close window" in lower or "window band karo" in lower:
            return {"intent": "close_active_window", "entities": {}, "raw": cmd}
        if "switch window" in lower or "alt tab" in lower or "window badlo" in lower:
            return {"intent": "switch_window", "entities": {}, "raw": cmd}

        # ======================================================================
        # 11b. CLIPBOARD & QUICK NOTES
        # ======================================================================
        if any(w in lower for w in ["read clipboard", "clipboard parho", "clipboard sunao", "what is on clipboard"]):
            return {"intent": "read_clipboard", "entities": {}, "raw": cmd}

        note_match = re.search(r"\b(?:take\s+a?\s*note|note\s+likho|note\s+banao|save\s+note)\s*:\s*(.+)$", cmd, re.IGNORECASE)
        if not note_match:
            note_match = re.search(r"\b(?:take\s+a?\s*note|note\s+likho|note\s+banao)\s+(.+)$", cmd, re.IGNORECASE)
        if note_match:
            return {"intent": "take_quick_note", "entities": {"text": note_match.group(1).strip()}, "raw": cmd}

        if any(w in lower for w in ["read notes", "show notes", "notes sunao", "notes parho", "my notes"]):
            return {"intent": "get_all_notes", "entities": {}, "raw": cmd}

        # ======================================================================
        # 12. MEDIA CONTROL
        # ======================================================================
        if lower in ["play", "pause", "resume", "play music", "pause music", "stop music", "gaana lagao", "gaana roko"]:
            return {"intent": "media_play_pause", "entities": {}, "raw": cmd}
        if "next song" in lower or "next track" in lower or "skip song" in lower or "agla gaana" in lower:
            return {"intent": "media_next", "entities": {}, "raw": cmd}
        if "previous song" in lower or "prev track" in lower or "previous track" in lower or "pichla gaana" in lower:
            return {"intent": "media_prev", "entities": {}, "raw": cmd}

        # ======================================================================
        # 13. MOUSE & KEYBOARD EMULATION
        # ======================================================================
        type_match = re.search(r"\b(?:type|write|likho)\s+(.+)$", cmd, re.IGNORECASE)
        if type_match and not any(k in lower for k in ["code", "document", "email"]):
            return {"intent": "type_text", "entities": {"text": type_match.group(1).strip()}, "raw": cmd}

        press_match = re.search(r"\bpress\s+(enter|space|escape|esc|tab|backspace|up|down|left|right)\b", lower)
        if press_match:
            return {"intent": "press_key", "entities": {"key": press_match.group(1)}, "raw": cmd}

        if lower in ["click", "left click", "mouse click", "click karo"]:
            return {"intent": "mouse_click", "entities": {}, "raw": cmd}

        # ======================================================================
        # 14. SYSTEM STATE & SENSITIVE POWER (Urdu & English)
        # ======================================================================
        if any(w in lower for w in ["system status", "battery", "cpu usage", "ram usage", "pc specs", "status batao"]):
            return {"intent": "system_status", "entities": {}, "raw": cmd}

        if "shutdown" in lower or "shut down" in lower or "pc band kardo" in lower or "computer band" in lower:
            return {"intent": "shutdown_system", "entities": {}, "raw": cmd}
        if "restart" in lower or "reboot" in lower or "restart kardo" in lower:
            return {"intent": "restart_system", "entities": {}, "raw": cmd}
        if "sleep" in lower and ("pc" in lower or "computer" in lower or lower == "sleep" or "sulado" in lower):
            return {"intent": "sleep_system", "entities": {}, "raw": cmd}
        if "lock" in lower and ("pc" in lower or "screen" in lower or "computer" in lower or "workstation" in lower):
            return {"intent": "lock_system", "entities": {}, "raw": cmd}

        # ======================================================================
        # 14.5 AUTONOMOUS CONTENT TEAM INTENTS
        # ======================================================================
        hook_match = re.search(r"\b(?:generate|create|write)\s+(?:viral\s+)?hooks?\s+(?:for|about|on)\s+(.+)$", lower)
        if hook_match:
            return {"intent": "generate_hooks", "entities": {"topic": hook_match.group(1).strip()}, "raw": cmd}

        script_match = re.search(r"\b(?:create|write|generate)\s+(?:tiktok|reels?|shorts?|video)\s+scripts?\s+(?:for|about|on)\s+(.+)$", lower)
        if script_match:
            return {"intent": "generate_script", "entities": {"topic": script_match.group(1).strip()}, "raw": cmd}

        carousel_match = re.search(r"\b(?:create|write|generate)\s+(?:carousel|slides?|thread)\s+(?:for|about|on)\s+(.+)$", lower)
        if carousel_match:
            return {"intent": "generate_carousel", "entities": {"topic": carousel_match.group(1).strip()}, "raw": cmd}

        calendar_match = re.search(r"\b(?:create|generate|plan)\s+(?:30\s*day\s+|monthly\s+)?content\s+calendar\s+(?:for|about|on)\s+(.+)$", lower)
        if calendar_match:
            return {"intent": "generate_calendar", "entities": {"niche": calendar_match.group(1).strip()}, "raw": cmd}

        repurpose_match = re.search(r"\brepurpose\s+(?:content\s+)?(?:about|on|for)?\s*(.+)$", lower)
        if repurpose_match:
            return {"intent": "repurpose_content", "entities": {"idea": repurpose_match.group(1).strip()}, "raw": cmd}

        # ======================================================================
        # 15. FALLBACK TO AI BRAIN
        # ======================================================================
        return {
            "intent": "ai_query",
            "entities": {"query": cmd},
            "raw": cmd
        }

    def _resolve_app(self, text: str) -> Optional[str]:
        text = text.lower().strip()
        if text in self.app_aliases:
            return self.app_aliases[text]
        for alias, app_name in self.app_aliases.items():
            if alias in text:
                return app_name
        return None
