"""
================================================================================
👑 BASIT JARVIS AI — HUMAN VOICE INTERACTION LOOP
================================================================================
Yahi hai asli JARVIS ka dil:

  1. "Hey Jarvis" suno  →  wake word detection
  2. Mic se command suno  →  faster-whisper STT
  3. Command samjho  →  ConversationalBrain / AI
  4. Jawab do VOICE mein  →  pyttsx3 TTS
  5. Waapis sun'na shuru  →  loop repeat

Chalao: python jarvis_voice.py
Rokne ke liye: Ctrl+C
================================================================================
"""

import sys
import os
import time
import json
import threading
import requests
import logging

# Force UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s [%(name)s] %(message)s'
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

JARVIS_URL = "http://localhost:8888/api/command"
WAKE_WORDS  = ["hey jarvis", "jarvis", "basit", "oi jarvis", "hey basit"]

# ─────────────────────────────────────────────────────────────────────────────
# CONSOLE COLORS
# ─────────────────────────────────────────────────────────────────────────────
CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def banner():
    print(f"""{BOLD}{CYAN}
╔══════════════════════════════════════════════════════════════════╗
║   👑 BASIT JARVIS AI — REAL HUMAN VOICE INTERACTION LOOP        ║
║   Say "Hey Jarvis" to wake me up — I'm always listening!        ║
╚══════════════════════════════════════════════════════════════════╝{RESET}
""")

# ─────────────────────────────────────────────────────────────────────────────
# TTS — SPEAK
# ─────────────────────────────────────────────────────────────────────────────
_tts_engine = None
_tts_lock   = threading.Lock()

def _init_tts():
    global _tts_engine
    try:
        import pyttsx3
        _tts_engine = pyttsx3.init()
        _tts_engine.setProperty('rate', 175)
        _tts_engine.setProperty('volume', 0.95)
        # Try to set a clear English voice
        voices = _tts_engine.getProperty('voices')
        for v in voices:
            if 'english' in v.name.lower() or 'david' in v.name.lower() or 'zira' in v.name.lower():
                _tts_engine.setProperty('voice', v.id)
                break
        print(f"{GREEN}✅ TTS (pyttsx3) ready{RESET}")
    except Exception as e:
        print(f"{YELLOW}⚠️  pyttsx3 not available ({e}) — text-only mode{RESET}")
        _tts_engine = None

def speak(text: str):
    """Speak text out loud AND print it."""
    # Clean text for speaking (remove markdown/emoji)
    import re
    clean = re.sub(r'[*_`#\[\]()🔥✅❌⚡👑📱💻🧠📄🔒]', '', text)
    clean = re.sub(r'https?://\S+', 'link', clean)
    clean = clean[:400]  # max 400 chars for voice

    print(f"\n{BOLD}{GREEN}🤖 JARVIS: {RESET}{text[:200]}")

    if _tts_engine:
        try:
            with _tts_lock:
                _tts_engine.say(clean)
                _tts_engine.runAndWait()
        except Exception as e:
            pass  # Silent fail — text already printed

# ─────────────────────────────────────────────────────────────────────────────
# STT — LISTEN (mic)
# ─────────────────────────────────────────────────────────────────────────────
_stt_model  = None
_stt_whisper = None
_stt_sr = None

def toast_notify(title: str, msg: str):
    """Sends native Windows 11 toast notification."""
    def _fire():
        try:
            from win11toast import toast
            toast(title, msg)
        except Exception:
            try:
                from winotify import Notification
                n = Notification(app_id="Basit Jarvis Voice", title=title, msg=msg)
                n.show()
            except Exception:
                pass
    threading.Thread(target=_fire, daemon=True).start()

def _init_stt():
    global _stt_whisper, _stt_sr
    try:
        from faster_whisper import WhisperModel
        print(f"{CYAN}⏳ Loading faster-whisper base model...{RESET}")
        _stt_whisper = WhisperModel("base", device="cpu", compute_type="int8")
        print(f"{GREEN}✅ faster-whisper STT ready (base, CPU, int8){RESET}")
    except Exception as e:
        print(f"{YELLOW}⚠️ faster-whisper not available: {e}{RESET}")
        _stt_whisper = None

    try:
        import speech_recognition as sr
        _stt_sr = sr.Recognizer()
        print(f"{GREEN}✅ SpeechRecognition STT ready (Google API fallback){RESET}")
    except Exception as e:
        print(f"{YELLOW}⚠️ SpeechRecognition not available: {e}{RESET}")
        _stt_sr = None

def listen_mic(timeout: float = 8.0, sample_rate: int = 16000) -> str:
    """Record from mic and return transcribed text with robust fallback."""
    # 1. Try faster-whisper
    if _stt_whisper is not None:
        try:
            import sounddevice as sd
            import numpy as np
            import io, wave

            print(f"{CYAN}🎤 Listening (Whisper)...{RESET}", end=" ", flush=True)
            duration = timeout
            audio_data = sd.rec(
                int(duration * sample_rate),
                samplerate=sample_rate,
                channels=1,
                dtype='int16'
            )
            # Wait with silence cutoff
            start = time.time()
            silence_count = 0
            chunk = int(sample_rate * 0.3)
            idx = 0
            while time.time() - start < duration:
                time.sleep(0.3)
                idx += chunk
                if idx >= len(audio_data):
                    break
                segment = audio_data[max(0, idx-chunk):idx]
                rms = float(np.sqrt(np.mean(segment.astype(np.float32)**2)))
                if rms < 300:
                    silence_count += 1
                else:
                    silence_count = 0
                if silence_count >= 5 and idx > sample_rate:
                    break

            sd.stop()
            actual = audio_data[:idx].flatten()
            if len(actual) >= sample_rate * 0.3:
                buf = io.BytesIO()
                with wave.open(buf, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(sample_rate)
                    wf.writeframes(actual.tobytes())
                buf.seek(0)

                segments, _ = _stt_whisper.transcribe(buf, language=None, beam_size=3)
                text = " ".join(s.text.strip() for s in segments).strip()
                if text:
                    print(f"{YELLOW}📝 Heard: \"{text}\"{RESET}")
                    return text
        except Exception as e:
            print(f"{YELLOW}⚠️ Whisper error ({e}), trying Google STT fallback...{RESET}")

    # 2. Try SpeechRecognition (Google)
    if _stt_sr is not None:
        try:
            import speech_recognition as sr
            with sr.Microphone() as source:
                print(f"{CYAN}🎤 Listening (Google STT)...{RESET}")
                _stt_sr.adjust_for_ambient_noise(source, duration=0.4)
                audio = _stt_sr.listen(source, timeout=timeout, phrase_time_limit=8)
            text = _stt_sr.recognize_google(audio)
            if text:
                print(f"{YELLOW}📝 Heard (Google): \"{text}\"{RESET}")
                return text
        except Exception:
            pass

    return ""


# ─────────────────────────────────────────────────────────────────────────────
# WAKE WORD DETECTION
# ─────────────────────────────────────────────────────────────────────────────
def check_wake_word(text: str) -> bool:
    t = text.lower().strip()
    return any(w in t for w in WAKE_WORDS)

def listen_for_wake_word() -> bool:
    """Quick short listen to check for wake word."""
    text = listen_mic(timeout=4.0)
    if not text:
        return False
    if check_wake_word(text):
        return True
    return False

# ─────────────────────────────────────────────────────────────────────────────
# SEND COMMAND TO JARVIS SERVER
# ─────────────────────────────────────────────────────────────────────────────
def ask_jarvis(command: str) -> str:
    """Send command to Jarvis server, get response text."""
    try:
        resp = requests.post(
            JARVIS_URL,
            json={"command": command},
            timeout=30
        )
        data = resp.json()
        return data.get("speak") or data.get("response") or data.get("summary") or "Command received."
    except requests.exceptions.ConnectionError:
        return "Server nahi mila bhai — pehle node server.js chalao!"
    except Exception as e:
        return f"Kuch masla aa gaya: {str(e)[:80]}"

# ─────────────────────────────────────────────────────────────────────────────
# LOCAL QUICK RESPONSES (no server round-trip needed)
# ─────────────────────────────────────────────────────────────────────────────
QUICK_RESPONSES = {
    "kese ho": "Main bilkul theek hoon Basit bhai, poora active! Aap sunao, kya karna hai aaj?",
    "how are you": "I'm fully operational and ready, Boss! What shall we build today?",
    "kya ho raha": "Main hamesha aapke liye available hoon bhai! Bas ek awaaz do.",
    "shukriya": "Arre koi baat nahi bhai! Yahi toh mera kaam hai! Aur kuch?",
    "thanks": "Pleasure is mine, Boss! Anything else?",
    "good morning": "Good morning Basit bhai! Aaj bhi zabardast din hoga — kya plan hai?",
    "good night": "Good night bhai! Rest well — main hamesha here hoon jab zaroorat ho.",
    "kon ho tum": "Main Basit Jarvis hoon — aapka sovereign AI assistant, hamesha ready!",
    "who are you": "I'm Basit Jarvis — your personal AI, always at your service!",
    "bore ho raha": "Chill mode! Chalo kuch naya banate hain ya main koi idea dun?",
    "stop": "Ji bhai, sun raha hoon. Kuch aur kaam hai toh batao.",
    "bye": "Khuda hafiz Basit bhai! Jab zaroorat ho — bas 'Hey Jarvis' kaho!",
}

def check_quick_response(text: str) -> str:
    t = text.lower()
    for key, val in QUICK_RESPONSES.items():
        if key in t:
            return val
    return ""

_force_command_event = threading.Event()

def _trigger_hotkey():
    print(f"\n{BOLD}{GREEN}🔥 [HOTKEY] Ctrl+Shift+J pressed! Activating command mode...{RESET}")
    toast_notify("Jarvis Hotkey Activated ⚡", "Sun raha hoon Basit bhai!")
    _force_command_event.set()

def setup_services():
    """Starts background global hotkey and dropzone watcher."""
    try:
        import keyboard
        keyboard.add_hotkey("ctrl+shift+j", _trigger_hotkey)
        print(f"{GREEN}✅ Global Hotkey [Ctrl+Shift+J] active! Press anytime.{RESET}")
    except Exception as e:
        print(f"{YELLOW}⚠️ Global Hotkey not hooked ({e}){RESET}")

    try:
        from modules.dropzone_watcher import start_dropzone_watcher
        start_dropzone_watcher(block=False)
        print(f"{GREEN}✅ Auto Dropzone Watcher active (E:\\basit-jarvis-ai\\dropzone){RESET}")
    except Exception as e:
        print(f"{YELLOW}⚠️ Dropzone Watcher note: {e}{RESET}")

# ─────────────────────────────────────────────────────────────────────────────
# MAIN VOICE LOOP
# ─────────────────────────────────────────────────────────────────────────────
def voice_loop():
    """Main infinite loop — listens, understands, responds."""
    setup_services()
    toast_notify("Basit Jarvis AI 👑", "Voice OS is online & listening for 'Hey Jarvis'!")
    speak("Assalam o Alaikum Basit bhai! Main Jarvis hoon — poora active aur ready. Bas 'Hey Jarvis' kaho aur main sun lunga!")

    mode = "wake_word"  # Modes: wake_word, command

    while True:
        try:
            if _force_command_event.is_set():
                _force_command_event.clear()
                speak("Haan bhai, batao! Main sun raha hoon.")
                mode = "command"

            if mode == "wake_word":
                # ── PHASE 1: Listen for wake word ──────────────────────────
                print(f"\n{CYAN}👂 [{mode.upper()}] Listening for 'Hey Jarvis' (or press Ctrl+Shift+J)...{RESET}")
                heard = listen_mic(timeout=5.0)

                if _force_command_event.is_set():
                    _force_command_event.clear()
                    speak("Haan bhai, batao!")
                    mode = "command"
                    continue

                if not heard:
                    continue

                if check_wake_word(heard):
                    # Wake word detected!
                    print(f"{GREEN}🔔 WAKE WORD DETECTED! '{heard}'{RESET}")
                    toast_notify("Wake Word Detected 🔔", f"Heard: '{heard}'")
                    speak("Haan bhai, batao! Main sun raha hoon.")
                    mode = "command"
                else:
                    # No wake word — maybe they said something without wake word
                    # Check if it's a direct command anyway
                    qr = check_quick_response(heard)
                    if qr:
                        speak(qr)

            elif mode == "command":
                # ── PHASE 2: Listen for actual command ─────────────────────
                print(f"\n{YELLOW}🎯 [{mode.upper()}] Waiting for your command...{RESET}")
                command = listen_mic(timeout=10.0)

                if not command or len(command.strip()) < 2:
                    speak("Sunai nahi diya bhai, dobara bolo!")
                    mode = "wake_word"
                    continue

                print(f"\n{BOLD}📨 COMMAND: \"{command}\"{RESET}")

                # Check for stop/exit commands
                if any(x in command.lower() for x in ["stop listening", "be quiet", "chup", "band karo", "exit", "quit"]):
                    speak("Theek hai bhai, ab main quiet mode mein ja raha hoon. Jab chahein 'Hey Jarvis' kaho!")
                    mode = "wake_word"
                    continue

                # Quick local response first (no latency)
                qr = check_quick_response(command)
                if qr:
                    speak(qr)
                    mode = "wake_word"
                    continue

                # Send to Jarvis server
                speak("Ji bhai, kaam kar raha hoon!")
                print(f"{CYAN}⚡ Sending to Jarvis server...{RESET}")

                response = ask_jarvis(command)
                speak(response)
                toast_notify("Task Completed ✅", command[:60])

                # Stay in command mode for follow-up
                mode = "wake_word"


        except KeyboardInterrupt:
            speak("Jarvis shut down ho raha hai. Khuda hafiz Basit bhai!")
            break
        except Exception as e:
            print(f"{RED}⚠️ Loop error: {e}{RESET}")
            time.sleep(1)
            mode = "wake_word"

# ─────────────────────────────────────────────────────────────────────────────
# KEYBOARD MODE (no mic available)
# ─────────────────────────────────────────────────────────────────────────────
def keyboard_loop():
    """Text chat mode — type commands, Jarvis responds with voice+text."""
    print(f"\n{YELLOW}⌨️  KEYBOARD MODE — Type your commands below{RESET}")
    print(f"{CYAN}   (Type 'exit' to quit){RESET}\n")
    speak("Keyboard mode active! Type your commands and I'll respond.")

    while True:
        try:
            user_input = input(f"{BOLD}{YELLOW}You: {RESET}").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "bye"]:
                speak("Khuda hafiz Basit bhai! Main hamesha ready hoon.")
                break

            # Quick local response
            qr = check_quick_response(user_input)
            if qr:
                speak(qr)
                continue

            # Server
            speak("Ji bhai, process kar raha hoon...")
            response = ask_jarvis(user_input)
            speak(response)

        except KeyboardInterrupt:
            speak("Khuda hafiz!")
            break

# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Basit Jarvis Voice Loop")
    parser.add_argument("--mode", choices=["voice", "keyboard"], default="voice",
                        help="'voice' = mic+speaker, 'keyboard' = type+speak")
    parser.add_argument("--no-tts", action="store_true", help="Disable voice output")
    args = parser.parse_args()

    banner()

    # Init TTS
    if not args.no_tts:
        _init_tts()
    else:
        print(f"{YELLOW}⚠️  TTS disabled (--no-tts){RESET}")

    # Init STT if voice mode
    if args.mode == "voice":
        _init_stt()

    print(f"\n{GREEN}{'='*60}{RESET}")
    print(f"{BOLD}Mode: {args.mode.upper()} | TTS: {'ON' if not args.no_tts else 'OFF'}{RESET}")
    print(f"{GREEN}{'='*60}{RESET}\n")

    if args.mode == "voice":
        voice_loop()
    else:
        keyboard_loop()
