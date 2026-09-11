"""
================================================================================
👑 BASIT JARVIS AI VOICE ASSISTANT — MASTER ORCHESTRATOR
================================================================================
World-class autonomous desktop AI assistant integrating all 13 core pillars:
1. Wake Word Detection ('Hey Jarvis' / 'Basit')
2. Speech-to-Text (Real-time Whisper)
3. Natural Language Understanding (Intent & Entity Parsing)
4. System Control Layer (Apps, Volume, Brightness, Files, Screenshots)
5. Text-to-Speech (pyttsx3 / ElevenLabs)
6. Context Memory (Multi-turn session history & pronoun resolution)
7. Multi-App Automation (Web Browser + MS Office win32com)
8. AI Brain Integration (OpenAI GPT-4o / Claude 3.5 / Local LLM)
9. Custom Command Macros ('start coding mode', 'focus mode')
10. Security Layer (Voice biometrics & confirmation on sensitive commands)
11. Hotkey Fallback (Global Ctrl+Shift+J)
12. Cross-App Notification Reader (WhatsApp, Slack, Outlook)
13. Background / System Tray Mode (pystray silent background daemon)
"""

import os
import sys
import json
import time
import signal
import logging
from typing import Dict, Any, Optional

# Load environment variables if .env exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Setup unified colorful logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("Jarvis.Core")

# Import all 13 modules
from modules.wake_word import WakeWordDetector
from modules.stt import SpeechToText
from modules.nlu import NaturalLanguageUnderstanding
from modules.system_control import SystemControl
from modules.tts import TextToSpeech
from modules.context_memory import ContextMemory
from modules.multi_app_automation import MultiAppAutomation
from modules.ai_brain import AIBrain
from modules.macros import MacroEngine
from modules.security import SecurityLayer
from modules.hotkey_listener import HotkeyListener
from modules.notification_reader import NotificationReader
from modules.tray_mode import SystemTrayApp
from modules.content_team import ContentTeam
from modules.basit_engines import BasitEngines


class BasitJarvis:
    def __init__(self, config_path: Optional[str] = None):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = config_path or os.path.join(self.base_dir, "config.json")
        self.config = self._load_config()

        logger.info(f"Initializing Basit Jarvis AI for owner: {self.config.get('jarvis', {}).get('owner', 'Basit')}...")

        # 1. System Control
        self.system = SystemControl(apps_map=self.config.get("apps", {}))

        # 2. Text-to-Speech
        tts_cfg = self.config.get("tts", {})
        self.tts = TextToSpeech(
            engine=tts_cfg.get("engine", "pyttsx3"),
            voice_index=tts_cfg.get("voice_index", 0),
            rate=tts_cfg.get("rate", 175),
            volume=tts_cfg.get("volume", 0.95),
            elevenlabs_api_key=tts_cfg.get("elevenlabs_api_key", ""),
            elevenlabs_voice_id=tts_cfg.get("elevenlabs_voice_id", "21m00Tcm4TlvDq8ikWAM")
        )

        # 3. Context Memory
        self.memory = ContextMemory(max_history=self.config.get("system", {}).get("context_memory_size", 25))

        # 4. Multi-App Automation
        self.automation = MultiAppAutomation()

        # 5. AI Brain
        ai_cfg = self.config.get("ai_brain", {})
        self.brain = AIBrain(
            provider=ai_cfg.get("provider", "openai"),
            openai_api_key=ai_cfg.get("openai_api_key", ""),
            anthropic_api_key=ai_cfg.get("anthropic_api_key", ""),
            model_openai=ai_cfg.get("model_openai", "gpt-4o"),
            model_anthropic=ai_cfg.get("model_anthropic", "claude-3-5-sonnet-20241022"),
            system_prompt=ai_cfg.get("system_prompt"),
            cluster_cfg=self.config.get("cluster", {})
        )

        # 5b. Autonomous Basit Engines (/basit1, /basit2, /basit3, /basitloop)
        self.basit_engines = BasitEngines(ai_brain=self.brain, default_dir=self.base_dir)

        # 6. Natural Language Understanding
        self.nlu = NaturalLanguageUnderstanding(app_aliases=self.config.get("apps", {}))

        # 7. Macros Engine
        self.macros = MacroEngine(
            macros_path=os.path.join(self.base_dir, "macros.json"),
            action_executor=self._execute_macro_action
        )

        # 8. Security Layer
        sec_cfg = self.config.get("security", {})
        self.security = SecurityLayer(
            voice_auth_enabled=sec_cfg.get("voice_auth_enabled", False),
            voice_auth_threshold=sec_cfg.get("voice_auth_threshold", 0.75),
            sensitive_commands=sec_cfg.get("sensitive_commands"),
            require_confirmation=sec_cfg.get("require_confirmation", True)
        )

        # 9. Speech-to-Text
        stt_cfg = self.config.get("stt", {})
        self.stt = SpeechToText(
            model_size=stt_cfg.get("model_size", "base"),
            device=stt_cfg.get("device", "cpu"),
            compute_type=stt_cfg.get("compute_type", "int8"),
            language=stt_cfg.get("language", "en"),
            silence_threshold=stt_cfg.get("silence_threshold", 450),
            silence_duration=stt_cfg.get("silence_duration", 1.3)
        )

        # 10. Wake Word Detector
        ww_cfg = self.config.get("wake_word", {})
        self.wake_detector = WakeWordDetector(
            wake_words=self.config.get("jarvis", {}).get("wake_words", ["hey jarvis", "basit"]),
            threshold=ww_cfg.get("threshold", 0.65),
            on_wake=self.on_wake_triggered
        )

        # 11. Global Hotkey
        hotkey_str = self.config.get("jarvis", {}).get("hotkey", "ctrl+shift+j")
        self.hotkey = HotkeyListener(hotkey=hotkey_str, on_trigger=self.on_wake_triggered)

        # 12. Notification Reader
        self.notifications = NotificationReader(
            enabled=self.config.get("system", {}).get("notification_reading", True),
            on_notification=self.on_notification_received
        )

        # 13. System Tray
        self.tray = SystemTrayApp(
            on_trigger=self.on_wake_triggered,
            on_toggle_mute=self.toggle_mute,
            on_exit=self.shutdown
        )

        # 14. Autonomous Content Team Squad
        self.content_team = ContentTeam(
            vault_dir=os.path.join(self.base_dir, "content_vault"),
            ai_brain=self.brain
        )

        self._running = False
        self._is_listening_command = False

    def _load_config(self) -> Dict[str, Any]:
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    # ---------------------------------------------------------
    # LIFECYCLE CONTROLS
    # ---------------------------------------------------------
    def start(self, cli_mode: bool = False):
        """Starts Basit Jarvis AI."""
        self._running = True
        print("\n" + "=" * 60)
        print("👑 BASIT JARVIS AI VOICE ASSISTANT — ONLINE 👑")
        print(f"Owner: {self.config.get('jarvis', {}).get('owner', 'Basit')}")
        print("Wake words: 'Hey Jarvis', 'Basit', 'Jarvis'")
        print("Fallback Hotkey: [CTRL + SHIFT + J]")
        print("=" * 60 + "\n")

        # Startup greeting
        greeting = f"Basit Jarvis online and fully operational, sir. How may I assist you?"
        self.tts.speak(greeting)

        # Start listeners
        self.wake_detector.start()
        self.hotkey.start()
        self.notifications.start()
        if self.config.get("system", {}).get("tray_mode", True) and not cli_mode:
            self.tray.start()

        # Hybrid Mode: Voice thread is active in background while terminal allows direct input
        print("🎙️ VOICE ENGINE ACTIVE: Listening for 'Hey Jarvis' / 'Basit' / [Ctrl+Shift+J]")
        print("⌨️ TERMINAL ACTIVE: You can also type commands directly below:\n")
        self._run_cli_loop()

    def shutdown(self):
        """Clean shutdown of all subsystems."""
        logger.info("Initiating Basit Jarvis shutdown...")
        self.tts.speak("Goodbye, sir. Shutting down systems.", block=True)
        self._running = False
        self.wake_detector.stop()
        self.hotkey.stop()
        self.notifications.stop()
        self.tray.stop()
        self.tts.stop()
        logger.info("Basit Jarvis offline.")

    def toggle_mute(self) -> bool:
        """Toggles wake word listening."""
        if self.wake_detector._paused:
            self.wake_detector.resume()
            self.tts.speak("Wake word detection resumed.")
            return False
        else:
            self.wake_detector.pause()
            self.tts.speak("Wake word detection muted.")
            return True

    # ---------------------------------------------------------
    # VOICE TRIGGER & PIPELINE DISPATCHER
    # ---------------------------------------------------------
    def on_wake_triggered(self):
        """Triggered upon wake word match or hotkey press. Enters multi-turn conversational loop."""
        if self._is_listening_command:
            return
        self._is_listening_command = True
        self.wake_detector.pause()

        try:
            # Human greeting acknowledgment
            self.tts.speak("Yes, Basit?")
            time.sleep(0.25)

            turns = 0
            max_turns = 8  # up to 8 continuous turns before auto-standby
            while self._running and turns < max_turns:
                # Record and transcribe user command
                command_text = self.stt.listen_and_transcribe(max_duration=8.0)
                if not command_text or not command_text.strip():
                    # No speech detected in follow-up window
                    break

                turns += 1
                logger.info(f"[CONVERSATION TURN {turns}]: \"{command_text}\"")
                response = self.process_command(command_text)

                # If user gave an exit / farewell phrase, end conversation naturally
                lower_cmd = command_text.lower()
                if any(w in lower_cmd for w in ["bye", "goodbye", "alvida", "chup", "shukriya", "thank you", "thanks", "bas itna hi", "standby"]):
                    break

                # Wait for TTS to finish speaking before listening for the user's next turn
                while self.tts.is_speaking:
                    time.sleep(0.15)
                time.sleep(0.3)

        except Exception as e:
            logger.error(f"Error in conversation processing: {e}")
        finally:
            self._is_listening_command = False
            self.wake_detector.resume()

    def process_command(self, text: str) -> str:
        """Core dispatcher parsing intents and executing commands."""
        logger.info(f"Processing command: \"{text}\"")

        # 1. Check if user is answering a pending sensitive confirmation
        if self.security._pending_confirmation:
            action = self.security.check_confirmation(text)
            if action:
                self.tts.speak("Confirmed. Executing action now, sir.")
                return self._execute_intent(action)
            else:
                self.tts.speak("Action cancelled, sir.")
                return "Cancelled"

        # 2. Parse text with NLU
        intents = self.nlu.parse(text)
        responses = []

        for item in intents:
            intent_name = item.get("intent")
            entities = item.get("entities", {})

            # 3. Security check: Is this action sensitive?
            if self.security.is_sensitive(intent_name) or self.security.is_sensitive(text):
                prompt = self.security.request_confirmation(item, prompt_callback=self.tts.speak)
                return prompt

            # 4. Execute Intent
            res = self._execute_intent(item)
            if res:
                responses.append(res)
                # Record to Context Memory
                self.memory.record_turn(text, intent_name, entities, res)

        final_response = " ".join(responses) if responses else "Done, sir."
        return final_response

    def _execute_intent(self, item: Dict[str, Any]) -> str:
        intent = item.get("intent")
        entities = item.get("entities", {})
        raw = item.get("raw", "")

        # Open App
        if intent == "open_app":
            app = entities.get("app")
            success = self.system.open_app(app)
            msg = f"Opening {app}, sir." if success else f"Could not launch {app}."
            self.tts.speak(msg)
            return msg

        # Close App
        elif intent == "close_app":
            app = entities.get("app")
            count = self.system.close_app(app)
            msg = f"Closed {app}, sir." if count > 0 else f"{app} was not running."
            self.tts.speak(msg)
            return msg

        # Web Search
        elif intent == "web_search":
            query = entities.get("query")
            engine = entities.get("engine", "google")
            self.automation.web_search(query, engine)
            msg = f"Searching {query} on {engine}, sir."
            self.tts.speak(msg)
            return msg

        # Open URL
        elif intent == "open_url":
            url = entities.get("url")
            self.automation.open_url(url)
            msg = f"Opening {url}."
            self.tts.speak(msg)
            return msg

        # Volume
        elif intent == "set_volume":
            if "action" in entities and entities["action"] == "mute":
                self.system.mute(True)
                msg = "Audio muted, sir."
            elif "action" in entities and entities["action"] == "unmute":
                self.system.mute(False)
                msg = "Audio unmuted, sir."
            else:
                val = entities.get("value", 50)
                self.system.set_volume(val)
                msg = f"Volume set to {val} percent."
            self.tts.speak(msg)
            return msg

        elif intent == "change_volume":
            delta = entities.get("delta", 10)
            self.system.change_volume(delta)
            msg = f"Volume adjusted."
            self.tts.speak(msg)
            return msg

        # Speaker / Voice Output ON/OFF Control
        elif intent == "toggle_speaker":
            state = entities.get("state", "toggle")
            if state == "off":
                self.tts.mute()
                msg = "Speaker and voice output muted, sir."
            elif state == "on":
                self.tts.unmute()
                msg = "Speaker and voice output active, sir."
                self.tts.speak(msg)
            else:
                is_muted = self.tts.toggle_mute()
                msg = "Speaker muted, sir." if is_muted else "Speaker unmuted, sir."
                if not is_muted:
                    self.tts.speak(msg)
            return msg

        # Brightness
        elif intent == "set_brightness":
            val = entities.get("value", 70)
            self.system.set_brightness(val)
            msg = f"Brightness adjusted to {val} percent."
            self.tts.speak(msg)
            return msg

        # Screenshot
        elif intent == "take_screenshot":
            path = self.system.take_screenshot()
            msg = "Screenshot captured and saved to your screenshots folder, sir." if path else "Screenshot failed."
            self.tts.speak(msg)
            return msg

        # File Search
        elif intent == "search_file":
            fn = entities.get("filename")
            loc = entities.get("location")
            matches = self.system.search_file(fn, loc)
            if matches:
                msg = f"Found {len(matches)} files matching {fn}. The first one is at {matches[0]}."
            else:
                msg = f"No files found matching {fn} in {loc}."
            self.tts.speak(msg)
            return msg

        # Run Macro
        elif intent == "run_macro":
            macro_name = entities.get("macro_name")
            success = self.macros.execute_macro(macro_name)
            msg = f"{macro_name.capitalize()} completed, sir." if success else f"Could not find macro {macro_name}."
            return msg

        # System Status
        elif intent == "system_status":
            stats = self.system.get_system_status()
            bat_info = f", Battery is at {stats['battery_percent']}%" if stats['battery_percent'] else ""
            msg = f"CPU is at {stats['cpu_percent']} percent, RAM is using {stats['ram_used_gb']} gigabytes{bat_info}."
            self.tts.speak(msg)
            return msg

        # Window Management
        elif intent == "minimize_all":
            self.system.minimize_all()
            return "Showing desktop, sir."

        elif intent == "minimize_active":
            self.system.minimize_active()
            return "Minimized window."

        elif intent == "maximize_active":
            self.system.maximize_active()
            return "Maximized window."

        elif intent == "close_active_window":
            self.system.close_active_window()
            return "Closed active window."

        elif intent == "switch_window":
            self.system.switch_window()
            return "Switched window."

        # Media Controls
        elif intent == "media_play_pause":
            self.system.media_play_pause()
            return "Toggled media playback."

        elif intent == "media_next":
            self.system.media_next()
            return "Skipped to next track."

        elif intent == "media_prev":
            self.system.media_prev()
            return "Playing previous track."

        # Keyboard / Mouse Emulation
        elif intent == "type_text":
            text_to_type = entities.get("text", "")
            self.system.type_text(text_to_type)
            return f"Typed: {text_to_type}"

        elif intent == "press_key":
            key = entities.get("key", "enter")
            self.system.press_key(key)
            return f"Pressed {key}."

        elif intent == "mouse_click":
            self.system.mouse_click()
            return "Clicked."

        # Sensitive System Power
        elif intent == "lock_system":
            self.system.lock_workstation()
            return "Workstation locked."

        elif intent == "sleep_system":
            self.system.sleep_system()
            return "System entering sleep mode, sir."

        elif intent == "shutdown_system":
            self.system.shutdown()
            return "Shutdown sequence initiated."

        elif intent == "restart_system":
            self.system.restart()
            return "Restart sequence initiated."

        # Content Team Operations
        elif intent == "generate_hooks":
            topic = entities.get("topic") or "business"
            if topic in ["that", "it", "that topic", "this"] and self.memory.last_topic:
                topic = self.memory.last_topic
            hooks = self.content_team.generate_viral_hooks(topic)
            summary = f"Generated {len(hooks)} viral hooks for {topic} and saved to Content Vault, sir."
            self.tts.speak(summary)
            return summary

        elif intent == "generate_script":
            topic = entities.get("topic") or "viral tech"
            if topic in ["that", "it", "that topic", "this"] and self.memory.last_topic:
                topic = self.memory.last_topic
            res = self.content_team.generate_video_script(topic)
            msg = f"Vertical video script for {topic} created and saved, sir."
            self.tts.speak(msg)
            return msg

        elif intent == "generate_carousel":
            topic = entities.get("topic") or "business growth"
            if topic in ["that", "it", "that topic", "this"] and self.memory.last_topic:
                topic = self.memory.last_topic
            res = self.content_team.generate_carousel(topic)
            msg = f"Carousel and thread blueprint for {topic} generated, sir."
            self.tts.speak(msg)
            return msg

        elif intent == "generate_calendar":
            niche = entities.get("niche") or "digital agency"
            if niche in ["that", "it", "that topic", "this"] and self.memory.last_topic:
                niche = self.memory.last_topic
            res = self.content_team.generate_30_day_calendar(niche)
            msg = f"30-day content calendar for {niche} generated and saved, sir."
            self.tts.speak(msg)
            return msg

        elif intent == "repurpose_content":
            idea = entities.get("idea") or "autonomous ai"
            if idea in ["that", "it", "that topic", "this"] and self.memory.last_topic:
                idea = self.memory.last_topic
            res = self.content_team.repurpose_idea(idea)
            msg = f"Content repurposed into 10 multi-channel assets, sir."
            self.tts.speak(msg)
            return msg

        # Basit 1: Ultra-Fast Coding
        elif intent == "basit1_code":
            prompt = entities.get("prompt", raw)
            res = self.basit_engines.dispatch("basit1", prompt, target_dir=self.base_dir)
            self.tts.speak(res.get("summary", "Code generation complete, sir."))
            return res.get("response", "Code generated.")

        # Basit 2: Deep Research
        elif intent == "basit2_research":
            query = entities.get("query", raw)
            res = self.basit_engines.dispatch("basit2", query)
            self.tts.speak(res.get("summary", "Research synthesis complete, sir."))
            return res.get("report", "Research complete.")

        # Basit 3: Security, Process Guard & Auto-Git
        elif intent == "basit3_guardian":
            action = entities.get("action", "all")
            res = self.basit_engines.dispatch("basit3", action, target_dir=self.base_dir)
            self.tts.speak(res.get("summary", "Security and process sweep complete, sir."))
            return res.get("summary", "Guardian execution complete.")

        # BasitLoop: Continuous Autonomous Looping Engine
        elif intent == "basit_loop":
            goal = entities.get("goal", raw)
            res = self.basit_engines.dispatch("basitloop", goal, target_dir=self.base_dir)
            self.tts.speak(res.get("summary", "BasitLoop completed, sir."))
            return res.get("summary", "Loop execution complete.")

        # Open Folder in File Explorer
        elif intent == "open_folder":
            folder = entities.get("folder", "desktop")
            success = self.system.open_folder(folder)
            msg = f"Opened {folder} folder, sir." if success else f"Could not find folder {folder}."
            self.tts.speak(msg)
            return msg

        # Git Command Execution
        elif intent == "run_git_command":
            args = entities.get("args", "status")
            res = self.system.run_git_command(args, repo_dir=self.base_dir)
            out = res.get("output", "")
            msg = f"Git {args}:\n{out[:250]}" if out else f"Git {args} executed."
            self.tts.speak(f"Git {args} finished, sir.")
            return msg

        # Terminal & PowerShell Execution
        elif intent == "run_terminal_command":
            cmd_str = entities.get("command", "")
            res = self.system.run_shell_command(cmd_str, cwd=self.base_dir)
            out = res.get("output", "")
            msg = f"Terminal result:\n{out[:250]}" if out else "Command executed, sir."
            self.tts.speak("Command finished, sir.")
            return msg

        # Window Snapping
        elif intent == "snap_window_left":
            self.system.snap_window_left()
            self.tts.speak("Snapped window left, sir.")
            return "Window snapped left."

        elif intent == "snap_window_right":
            self.system.snap_window_right()
            self.tts.speak("Snapped window right, sir.")
            return "Window snapped right."

        # Clipboard Management
        elif intent == "read_clipboard":
            text = self.system.get_clipboard_text()
            if text:
                msg = f"Your clipboard contains: {text[:150]}"
                self.tts.speak(msg)
                return text
            else:
                self.tts.speak("Clipboard is empty, sir.")
                return "Clipboard is empty."

        # Quick Notes
        elif intent == "take_quick_note":
            note_text = entities.get("text", "")
            self.system.take_quick_note(note_text)
            self.tts.speak("Note recorded and saved, sir.")
            return f"Note saved: '{note_text}'"

        elif intent == "get_all_notes":
            notes = self.system.get_all_notes()
            if notes:
                latest = notes[-3:]
                summary = " Here are your latest notes: " + "; ".join([n["text"] for n in latest])
                self.tts.speak(summary)
                return json.dumps(notes, indent=2)
            else:
                self.tts.speak("You have no saved notes, sir.")
                return "No notes found."

        # AI Brain Query
        elif intent == "ai_query":
            q = entities.get("query", raw)
            history = self.memory.get_conversation_history()
            reply = self.brain.ask(q, history)
            self.tts.speak(reply)
            return reply

        return "Command completed, sir."

    def _execute_macro_action(self, action: Dict[str, Any]):
        """Executes a single action within a macro."""
        atype = action.get("type")
        if atype == "open_app":
            self.system.open_app(action.get("app"))
        elif atype == "close_app":
            self.system.close_app(action.get("app"))
        elif atype == "set_volume":
            self.system.set_volume(action.get("value", 50))
        elif atype == "set_brightness":
            self.system.set_brightness(action.get("value", 70))
        elif atype == "speak":
            self.tts.speak(action.get("text", ""))
        elif atype == "open_url":
            self.automation.open_url(action.get("url"))
        elif atype == "shutdown":
            self.system.shutdown()

    def on_notification_received(self, app: str, title: str, message: str):
        """Triggered when a Windows notification arrives."""
        announcement = f"Notification from {app}: {title}. {message}"
        self.tts.speak(announcement)

    # ---------------------------------------------------------
    # CLI / INTERACTIVE TERMINAL LOOP
    # ---------------------------------------------------------
    def _run_cli_loop(self):
        """Allows interactive typing testing alongside voice."""
        print("💡 Interactive CLI Mode active. Type your command (or 'exit' to quit):")
        while self._running:
            try:
                user_input = input("You: ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ["exit", "quit"]:
                    self.shutdown()
                    break
                response = self.process_command(user_input)
                print(f"Jarvis: {response}\n")
            except (KeyboardInterrupt, EOFError):
                self.shutdown()
                break

    def _run_main_loop(self):
        """Background continuous thread keeper."""
        while self._running:
            time.sleep(0.5)


if __name__ == "__main__":
    cli_flag = "--cli" in sys.argv
    jarvis = BasitJarvis()
    try:
        jarvis.start(cli_mode=cli_flag)
    except KeyboardInterrupt:
        jarvis.shutdown()
