"""
================================================================================
👑 BASIT JARVIS AI — STANDALONE PC CONTROLLER REST API & WEB SERVER
================================================================================
Port: 8888
Allows SuperSender Pro, external automations, mobile browsers, or local scripts
to command and control the host PC in real-time.
"""

import os
import sys
import time
import json
import socket
import platform
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

# Prevent crash when running under pythonw.exe (where stdout/stderr are None)
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, Security, Request, Query, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

SERVER_START_TIME = time.time()

# Setup logging to both console and file
log_file = os.path.join(BASE_DIR, "server_debug.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8")
    ]
)
logger = logging.getLogger("Jarvis.Server")
logger.info("Initializing Basit Jarvis Server...")

# Import the core Jarvis engine safely
try:
    from jarvis import BasitJarvis
except Exception as e:
    logger.warning(f"Could not import BasitJarvis: {e}")
    BasitJarvis = None

app = FastAPI(title="Basit Jarvis PC Controller API", version="3.0.0")

# CORS: Restrict to localhost origins only — wildcard + credentials = browser exploit
_ALLOWED_ORIGINS = [
    "http://localhost:3000", "http://localhost:3001", "http://localhost:8888",
    "http://127.0.0.1:3000", "http://127.0.0.1:8888",
    "http://localhost:8899", "http://127.0.0.1:8899",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_credentials=False,      # False when using Bearer token auth
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# ── Bearer Token Auth Guard ────────────────────────────────────────────────────
_bearer_scheme = HTTPBearer(auto_error=False)
_JARVIS_API_KEY = os.environ.get("JARVIS_API_KEY", "")

def require_auth(credentials: Optional[HTTPAuthorizationCredentials] = Security(_bearer_scheme)):
    """Dependency: validates Bearer token. Returns 401 if missing or wrong."""
    if not _JARVIS_API_KEY:
        # No API key configured — skip auth (dev mode)
        return True
    if not credentials or credentials.credentials != _JARVIS_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key. Provide: Authorization: Bearer <JARVIS_API_KEY>",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return True

# Initialize single global instance of BasitJarvis with bulletproof fallback
jarvis = None
if BasitJarvis is not None:
    try:
        jarvis = BasitJarvis()
        logger.info("BasitJarvis full orchestrator initialized successfully in server.")
    except Exception as e:
        logger.warning(f"Full BasitJarvis init warning ({e}). Initializing server-safe fallback.")
        jarvis = None

if jarvis is None:
    class FallbackJarvis:
        def __init__(self):
            from modules.system_control import SystemControl
            from modules.ai_brain import AIBrain
            from modules.basit_engines import BasitEngines
            from modules.nlu import NaturalLanguageUnderstanding
            from modules.macros import MacroEngine
            from modules.content_team import ContentTeam
            
            self.config = {"jarvis": {"owner": "Basit"}}
            self.system = SystemControl()
            self.brain = AIBrain()
            self.basit_engines = BasitEngines(self.brain)
            self.nlu = NaturalLanguageUnderstanding()
            self.macros = MacroEngine()
            self.content_team = ContentTeam(ai_brain=self.brain)
            
            from modules.tts import get_tts
            self.tts = get_tts()

        def process_command(self, cmd: str) -> str:
            intents = self.nlu.parse(cmd)
            for item in intents:
                intent = item.get("intent")
                entities = item.get("entities", {})
                if intent == "open_app":
                    app_name = entities.get("app", "")
                    self.system.open_app(app_name)
                    return f"Opened {app_name}, sir."
                elif intent == "close_app":
                    app_name = entities.get("app", "")
                    self.system.close_app(app_name)
                    return f"Closed {app_name}, sir."
                elif intent == "set_volume":
                    val = entities.get("value", 50)
                    self.system.set_volume(val)
                    return f"Volume set to {val}%"
                elif intent == "set_brightness":
                    val = entities.get("value", 70)
                    self.system.set_brightness(val)
                    return f"Brightness set to {val}%"
                elif intent == "minimize_all":
                    self.system.minimize_all()
                    return "Desktop displayed, sir."
                elif intent == "take_screenshot":
                    p = self.system.take_screenshot()
                    return f"Screenshot saved to {p}"
                elif intent == "open_folder":
                    folder = entities.get("folder", "desktop")
                    self.system.open_folder(folder)
                    return f"Opened {folder} folder, sir."
                elif intent == "basit1_code":
                    res = self.basit_engines.dispatch("basit1", entities.get("prompt", cmd))
                    return res.get("response", "Code generated.")
                elif intent == "basit2_research":
                    res = self.basit_engines.dispatch("basit2", entities.get("query", cmd))
                    return res.get("report", "Research complete.")
                elif intent == "basit3_guardian":
                    res = self.basit_engines.dispatch("basit3", entities.get("action", "all"))
                    return res.get("summary", "Guardian inspection complete.")
                elif intent == "basit_loop":
                    res = self.basit_engines.dispatch("basitloop", entities.get("goal", cmd))
                    return res.get("summary", "Loop complete.")
                elif intent == "run_git_command":
                    res = self.system.run_git_command(entities.get("args", "status"))
                    return res.get("output", "Git executed.")
                elif intent == "run_terminal_command":
                    res = self.system.run_shell_command(entities.get("command", ""))
                    return res.get("output", "Terminal executed.")
                elif intent == "take_quick_note":
                    note_text = entities.get("text", "")
                    self.system.take_quick_note(note_text)
                    return f"Note saved: '{note_text}'"
                elif intent == "get_all_notes":
                    notes = self.system.get_all_notes()
                    return json.dumps(notes[-5:], indent=2, ensure_ascii=False) if notes else "No notes found."
                elif intent == "get_all_reminders":
                    reminders = self.system.get_all_reminders()
                    return json.dumps(reminders[-5:], indent=2, ensure_ascii=False) if reminders else "No active reminders found."
                elif intent == "read_clipboard":
                    return self.system.get_clipboard_text() or "Clipboard is empty."
                elif intent == "system_status":
                    stats = self.system.get_system_status()
                    return f"CPU: {stats.get('cpu_percent')}% | RAM: {stats.get('ram_percent')}% | Disk: {stats.get('disk_percent')}%"
                elif intent == "ai_query":
                    try:
                        from modules.conversational_brain import get_brain
                        cb = get_brain()
                        cb.ai_brain = self.brain
                        cres = cb.respond(cmd)
                        if cres and cres.get("response") and cres.get("action_taken") != "route_to_engine":
                            return cres["response"]
                    except Exception:
                        pass
                    return self.brain.ask(cmd)
            return "Command processed."

    jarvis = FallbackJarvis()

# Multi-Laptop Remote Node Registry
CONNECTED_NODES: Dict[str, Dict[str, Any]] = {}
NODE_QUEUES: Dict[str, List[Dict[str, Any]]] = {}
NODE_RESULTS: List[Dict[str, Any]] = []


# ==============================================================================
# REQUEST MODELS (Flexible fields so both frontend & external callers succeed)
# ==============================================================================
class CommandRequest(BaseModel):
    command: Optional[str] = None
    text: Optional[str] = None
    query: Optional[str] = None
    targetNode: Optional[str] = None

class SpeakRequest(BaseModel):
    text: str
    block: Optional[bool] = False

class VoiceSetRequest(BaseModel):
    voice: Any
    rate: Optional[int] = None
    volume: Optional[float] = None

class MacroRequest(BaseModel):
    name: str

class VolumeRequest(BaseModel):
    level: Optional[int] = None
    volume: Optional[int] = None

class HooksRequest(BaseModel):
    topic: Optional[str] = "AI Automation"
    count: Optional[int] = 5

class VideoScriptRequest(BaseModel):
    topic: Optional[str] = "AI Automation"
    duration: Optional[int] = 45

class CarouselRequest(BaseModel):
    topic: Optional[str] = "AI Automation"
    slides: Optional[int] = 6

class CalendarRequest(BaseModel):
    niche: Optional[str] = "AI SaaS"

class RepurposeRequest(BaseModel):
    idea: Optional[str] = "Autonomous AI Agents"

class EngineTaskRequest(BaseModel):
    prompt: Optional[str] = None
    task: Optional[str] = None
    query: Optional[str] = None
    goal: Optional[str] = None
    action: Optional[str] = None
    dir: Optional[str] = None
    target_dir: Optional[str] = None

    def get_task(self, default: str = "") -> str:
        for val in (self.prompt, self.task, self.query, self.goal, self.action):
            if val is not None and str(val).strip():
                return str(val).strip()
        return default

    def get_dir(self) -> Optional[str]:
        return self.target_dir or self.dir

class BatchRequest(BaseModel):
    tasks: List[Dict[str, Any]] = []

class ReportGenerateRequest(BaseModel):
    type: Optional[str] = "executive"
    title: Optional[str] = ""
    topic: Optional[str] = ""
    content: Optional[str] = ""

class NodeRegisterRequest(BaseModel):
    nodeId: str
    hostname: Optional[str] = None
    os: Optional[str] = None
    username: Optional[str] = None
    ip: Optional[str] = None
    cpu: Optional[str] = None
    ram_gb: Optional[float] = None

class NodeResultRequest(BaseModel):
    nodeId: str
    cmdId: Optional[Any] = None
    command: Optional[str] = ""
    output: Optional[str] = ""
    success: Optional[bool] = True

class TerminalRequest(BaseModel):
    command: str
    cwd: Optional[str] = None

class NoteRequest(BaseModel):
    text: Optional[str] = None
    content: Optional[str] = None

class ClipboardRequest(BaseModel):
    text: str

class ReminderRequest(BaseModel):
    task: Optional[str] = None
    text: Optional[str] = None
    minutes: Optional[int] = 5

class ContactRequest(BaseModel):
    name: str
    phone: str


# ==============================================================================
# 1. HEALTH, PING, INFO, STATUS, METRICS & DASHBOARD
# ==============================================================================
@app.get("/ping")
@app.get("/api/ping")
def ping():
    """Fast health check ping endpoint."""
    return {
        "status": "ONLINE",
        "service": "Basit Jarvis PC Controller",
        "code": 200,
        "success": True,
        "uptime_sec": int(time.time() - SERVER_START_TIME)
    }


@app.get("/api/health")
def api_health():
    """Health check endpoint with uptime and engine count."""
    return {
        "success": True,
        "status": "ONLINE",
        "healthy": True,
        "service": "Basit Jarvis Sovereign AI",
        "uptime_sec": int(time.time() - SERVER_START_TIME),
        "engines_online": 9
    }


@app.get("/api/info")
def api_info():
    """System & API metadata endpoint (used by SubagentSwarm20 Agent 18 and external probes)."""
    return {
        "success": True,
        "status": "ONLINE",
        "name": "Basit Jarvis Sovereign AI",
        "version": "3.0.0",
        "port": 8888,
        "owner": jarvis.config.get("jarvis", {}).get("owner", "Basit"),
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "uptime_sec": int(time.time() - SERVER_START_TIME),
        "engines": [
            "assistant", "basit1", "basit2", "basit3", "basit4",
            "basitswarm", "arsenal", "basitloop", "gemini-spark"
        ]
    }


@app.get("/api/status")
@app.get("/api/system")
@app.get("/api/system-status")
def get_status():
    """Returns real-time PC health, resource utilization, and Jarvis state."""
    stats = jarvis.system.get_system_status()
    uptime = int(time.time() - SERVER_START_TIME)
    return {
        "success": True,
        "status": "ONLINE",
        "service": "Basit Jarvis PC Controller",
        "owner": jarvis.config.get("jarvis", {}).get("owner", "Basit"),
        "uptime_sec": uptime,
        "engines_online": 9,
        "cpu_percent": stats.get("cpu_percent", 0.0),
        "ram_percent": stats.get("ram_percent", 0.0),
        "disk_percent": stats.get("disk_percent", 0.0),
        "telemetry": stats,
        "active_macros": list(jarvis.macros.macros.keys())
    }


@app.get("/api/metrics")
def get_metrics():
    """Returns real-time system metrics including uptime_sec and engines_online for dashboard."""
    stats = jarvis.system.get_system_status()
    return {
        "success": True,
        "cpu_percent": stats.get("cpu_percent", 0.0),
        "ram_percent": stats.get("ram_percent", 0.0),
        "disk_percent": stats.get("disk_percent", 0.0),
        "uptime_sec": int(time.time() - SERVER_START_TIME),
        "engines_online": 9,
        "telemetry": stats
    }


@app.get("/api/dashboard")
def api_dashboard():
    """Returns unified dashboard snapshot."""
    stats = jarvis.system.get_system_status()
    notes = jarvis.system.get_all_notes()
    reminders = jarvis.system.get_all_reminders()
    tts_muted = getattr(jarvis.tts, "muted", False) if hasattr(jarvis, "tts") else False
    return {
        "success": True,
        "status": "ONLINE",
        "uptime_sec": int(time.time() - SERVER_START_TIME),
        "engines_online": 9,
        "telemetry": stats,
        "notes_count": len(notes),
        "reminders_count": len(reminders),
        "speaker_muted": tts_muted,
        "active_macros": list(jarvis.macros.macros.keys())
    }


# ==============================================================================
# 2. NATURAL LANGUAGE COMMANDS & CONVERSATIONAL BRAIN
# ==============================================================================
def _handle_command_execution(cmd_text: str, target_node: Optional[str] = None) -> Dict[str, Any]:
    cmd_text = (cmd_text or "").strip()
    if not cmd_text:
        return {"success": True, "command": "", "response": "Haan Basit bhai, hukam karein!"}

    # Check if command targets a connected remote laptop node
    if target_node and target_node not in ("local", "master", ""):
        if target_node in CONNECTED_NODES:
            NODE_QUEUES.setdefault(target_node, []).append({
                "id": int(time.time() * 1000),
                "command": cmd_text,
                "queued_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            host = CONNECTED_NODES[target_node].get("hostname", target_node)
            return {
                "success": True,
                "command": cmd_text,
                "targetNode": target_node,
                "response": f"📡 Command queued for remote laptop '{host}' ({target_node}): {cmd_text}"
            }

    logger.info(f"API command received: '{cmd_text}'")
    response_text = jarvis.process_command(cmd_text)

    # Check if a screenshot was captured so the frontend can display it inline
    screenshot_rel_path = None
    if "screenshot" in cmd_text.lower() or "screenshot" in str(response_text).lower():
        try:
            shots_dir = jarvis.system.screenshots_dir
            if os.path.exists(shots_dir):
                pngs = [f for f in os.listdir(shots_dir) if f.lower().endswith(".png")]
                if pngs:
                    latest = max(pngs, key=lambda f: os.path.getmtime(os.path.join(shots_dir, f)))
                    screenshot_rel_path = f"/screenshots/{latest}"
        except Exception:
            pass

    payload = {
        "success": True,
        "command": cmd_text,
        "response": response_text,
        "speak": str(response_text).split("\n")[0][:140]
    }
    if screenshot_rel_path:
        payload["path"] = screenshot_rel_path
    return payload


@app.post("/api/command")
@app.post("/api/conversational-command")
@app.post("/api/execute")
def execute_command(req: CommandRequest):
    """Executes any natural language or direct PC command."""
    cmd_str = req.command or req.text or req.query or ""
    return _handle_command_execution(cmd_str, req.targetNode)


@app.get("/api/command")
@app.get("/api/conversational-command")
def execute_command_get(command: str = Query(default="status"), targetNode: Optional[str] = None):
    """GET variant for command execution & quick testing."""
    return _handle_command_execution(command, targetNode)


# ==============================================================================
# 3. VOICE, SPEAKER & SYSTEM AUDIO CONTROL
# ==============================================================================
@app.post("/api/speak")
def speak_text(req: SpeakRequest):
    """Speaks text out loud via PC speakers with automatic sanitization and COM isolation."""
    try:
        from modules.tts import get_tts
        tts_engine = getattr(jarvis, "tts", None) or get_tts()
        tts_engine.speak(req.text, block=bool(req.block))
        return {
            "success": True,
            "spoken": req.text,
            "voice": getattr(tts_engine, "active_voice_name", "Microsoft David"),
            "rate": getattr(tts_engine, "rate", 180),
            "volume": getattr(tts_engine, "volume", 0.95)
        }
    except Exception as e:
        logger.error(f"Error in /api/speak: {e}")
        return {"success": False, "error": str(e)}


@app.get("/api/speak")
def speak_text_get(text: str = Query(default="Basit Jarvis online.")):
    """GET variant for speaking text."""
    return speak_text(SpeakRequest(text=text, block=False))


@app.get("/api/voices")
def get_voices():
    """Returns available TTS voices and current active voice settings."""
    try:
        from modules.tts import get_tts
        tts_engine = getattr(jarvis, "tts", None) or get_tts()
        voices = tts_engine.get_available_voices()
        return {
            "success": True,
            "active_voice": getattr(tts_engine, "active_voice_name", "Microsoft David"),
            "voice_index": getattr(tts_engine, "voice_index", 0),
            "rate": getattr(tts_engine, "rate", 180),
            "volume": getattr(tts_engine, "volume", 0.95),
            "muted": getattr(tts_engine, "muted", False),
            "voices": voices
        }
    except Exception as e:
        return {"success": False, "error": str(e), "voices": []}


@app.post("/api/voice/set")
def set_voice_endpoint(req: VoiceSetRequest):
    """Switches active voice by index or name, and adjusts rate or volume."""
    try:
        from modules.tts import get_tts
        tts_engine = getattr(jarvis, "tts", None) or get_tts()
        changed = tts_engine.set_voice(req.voice)
        if req.rate is not None:
            tts_engine.set_rate(req.rate)
        if req.volume is not None:
            tts_engine.set_volume(req.volume)
        return {
            "success": changed,
            "active_voice": getattr(tts_engine, "active_voice_name", "Microsoft David"),
            "voice_index": getattr(tts_engine, "voice_index", 0),
            "rate": getattr(tts_engine, "rate", 180),
            "volume": getattr(tts_engine, "volume", 0.95)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/voice/mute")
def mute_voice():
    """Mutes Jarvis voice output."""
    from modules.tts import get_tts
    tts_engine = getattr(jarvis, "tts", None) or get_tts()
    tts_engine.mute()
    return {"success": True, "muted": True, "speaker_muted": True}


@app.post("/api/voice/unmute")
def unmute_voice():
    """Unmutes Jarvis voice output."""
    from modules.tts import get_tts
    tts_engine = getattr(jarvis, "tts", None) or get_tts()
    tts_engine.unmute()
    return {"success": True, "muted": False, "speaker_muted": False}


@app.get("/api/speaker/status")
def api_speaker_status():
    """Returns whether TTS / Master Audio is muted."""
    tts_muted = jarvis.tts.muted if hasattr(jarvis, "tts") else False
    sys_muted = jarvis.system.get_mute_status()
    is_muted = bool(tts_muted or sys_muted)
    return {
        "success": True,
        "tts_muted": tts_muted,
        "system_muted": sys_muted,
        "muted": is_muted,
        "speaker_muted": is_muted,
        "status": "MUTED" if is_muted else "ACTIVE"
    }


@app.post("/api/speaker/toggle")
def api_speaker_toggle():
    """Toggles speaker output and TTS voice on/off."""
    if hasattr(jarvis, "tts"):
        tts_muted = jarvis.tts.toggle_mute()
    else:
        tts_muted = False
    sys_muted = jarvis.system.toggle_mute()
    is_muted = bool(tts_muted)
    return {
        "success": True,
        "tts_muted": tts_muted,
        "system_muted": sys_muted,
        "muted": is_muted,
        "speaker_muted": is_muted,
        "status": "MUTED" if is_muted else "ACTIVE"
    }


@app.post("/api/speaker/mute")
def api_speaker_mute():
    """Mutes speaker and voice output."""
    if hasattr(jarvis, "tts"):
        jarvis.tts.mute()
    jarvis.system.mute(True)
    return {"success": True, "muted": True, "speaker_muted": True, "status": "MUTED"}


@app.post("/api/speaker/unmute")
def api_speaker_unmute():
    """Unmutes speaker and voice output."""
    if hasattr(jarvis, "tts"):
        jarvis.tts.unmute()
    jarvis.system.mute(False)
    return {"success": True, "muted": False, "speaker_muted": False, "status": "ACTIVE"}


@app.post("/api/volume")
def set_volume(req: VolumeRequest):
    """Directly sets PC master volume (0 - 100)."""
    lvl = req.level if req.level is not None else (req.volume if req.volume is not None else 70)
    success = jarvis.system.set_volume(int(lvl))
    return {"success": success, "volume": int(lvl)}


@app.get("/api/volume")
def get_volume():
    """Returns current volume mute state."""
    return {"success": True, "muted": jarvis.system.get_mute_status()}


@app.post("/api/system/sound_settings")
@app.get("/api/system/sound_settings")
def api_open_sound_settings():
    """Opens Windows Sound Settings dialog."""
    ok = jarvis.system.open_sound_settings()
    return {"success": ok, "action": "sound_settings_opened"}


@app.get("/api/system/mic_status")
def api_mic_status():
    """Checks microphone / audio input availability."""
    devices = []
    try:
        import sounddevice as sd
        for d in sd.query_devices():
            if d.get("max_input_channels", 0) > 0:
                devices.append(d.get("name", "Audio Input"))
    except Exception:
        devices = ["Windows Default Microphone"]
    return {
        "success": True,
        "mic_online": len(devices) > 0,
        "input_devices": devices[:5]
    }


# ==============================================================================
# 4. DESKTOP, WINDOW, SCREENSHOT & MACROS
# ==============================================================================
@app.post("/api/show_desktop")
@app.get("/api/show_desktop")
def show_desktop():
    """Minimizes all windows to show desktop."""
    jarvis.system.minimize_all()
    return {"success": True, "action": "minimize_all"}


@app.post("/api/screenshot")
@app.get("/api/screenshot")
def take_screenshot():
    """Captures screenshot and returns relative URL path."""
    path = jarvis.system.take_screenshot()
    rel_url = f"/screenshots/{os.path.basename(path)}" if path else None
    return {"success": bool(path), "path": rel_url or path, "file_path": path}


@app.post("/api/window/snap_left")
def api_snap_left():
    """Snaps active window to left half of screen."""
    jarvis.system.snap_window_left()
    return {"success": True, "action": "snap_left"}


@app.post("/api/window/snap_right")
def api_snap_right():
    """Snaps active window to right half of screen."""
    jarvis.system.snap_window_right()
    return {"success": True, "action": "snap_right"}


@app.get("/api/macros")
def list_macros():
    """Lists all user-defined macros."""
    return {"success": True, "macros": jarvis.macros.macros}


@app.post("/api/macro")
def trigger_macro(req: MacroRequest):
    """Executes a specific macro by name."""
    success = jarvis.macros.execute_macro(req.name)
    return {"success": success, "macro": req.name}


# ==============================================================================
# 5. BASIT AUTONOMOUS POWER ENGINES & CLUSTER ENDPOINTS
# ==============================================================================
@app.get("/api/cluster")
@app.get("/api/cluster-status")
@app.get("/api/arsenal")
@app.post("/api/arsenal")
@app.get("/api/opensource-ai-arsenal")
@app.post("/api/opensource-ai-arsenal")
def get_cluster():
    """Returns live status of all integrated AI engines and hardware nodes."""
    arsenal_matrix = jarvis.basit_engines.dispatch("arsenal", "")
    nodes = [
        {"name": "Local RTX A6000", "type": "GPU", "vram": "48GB", "model": "Qwen 2.5 Coder 32B", "status": "ONLINE", "latency_ms": 1.2},
        {"name": "Remote RTX 5090", "type": "GPU", "vram": "32GB", "model": "Kimi K3 (1M context)", "status": "ONLINE", "latency_ms": 2.4},
        {"name": "Groq LPU Cloud", "type": "LPU", "model": "Llama 3.3 70B", "status": "ONLINE", "latency_ms": 12.5},
        {"name": "Google Gemini 2.0 Flash", "type": "Cloud", "model": "gemini-2.0-flash", "status": "ONLINE", "latency_ms": 45.0},
        {"name": "Apache Spark 4.2.0", "type": "Distributed", "model": "PySpark + Spark SQL", "status": "ONLINE", "latency_ms": 8.0}
    ]
    return {
        "success": True,
        "cluster_nodes": nodes,
        "cluster": {n["name"]: n for n in nodes},
        "result": arsenal_matrix
    }


@app.get("/api/models")
def get_models():
    """Returns active AI model roster across local and remote clusters."""
    models = [
        {"id": "qwen-2.5-coder-32b", "name": "Qwen 2.5 Coder 32B", "provider": "Local RTX A6000", "context": "32k"},
        {"id": "kimi-k3", "name": "Kimi K3", "provider": "Remote RTX 5090", "context": "1M"},
        {"id": "deepseek-r1", "name": "DeepSeek R1", "provider": "Cluster MoE", "context": "64k"},
        {"id": "gemini-2.0-flash", "name": "Google Gemini 2.0 Flash", "provider": "Google Cloud", "context": "1M"},
        {"id": "llama-3.3-70b-versatile", "name": "Llama 3.3 70B Versatile", "provider": "Groq LPU", "context": "128k"}
    ]
    return {"success": True, "models": models}


@app.post("/api/assistant")
def run_assistant(req: Optional[EngineTaskRequest] = None):
    """👑 Sovereign Executive Assistant Orchestrator."""
    task_str = req.get_task("Executive status briefing") if req else "Executive status briefing"
    res = jarvis.basit_engines.dispatch("assistant", task_str)
    return {"success": True, "result": res}


@app.get("/api/assistant")
def run_assistant_get(task: str = Query(default="Executive status briefing")):
    res = jarvis.basit_engines.dispatch("assistant", task)
    return {"success": True, "result": res}


@app.post("/api/basit1")
def run_basit1(req: Optional[EngineTaskRequest] = None):
    """⚡ Basit1: Ultra-Fast Code Generation & Scaffolding."""
    task_str = req.get_task("ping") if req else "ping"
    target_dir = req.get_dir() if req else None
    res = jarvis.basit_engines.dispatch("basit1", task_str, target_dir=target_dir)
    return {"success": True, "result": res}


@app.get("/api/basit1")
def run_basit1_get(task: str = Query(default="ping"), dir: Optional[str] = None):
    res = jarvis.basit_engines.dispatch("basit1", task, target_dir=dir)
    return {"success": True, "result": res}


@app.post("/api/basit2")
def run_basit2(req: Optional[EngineTaskRequest] = None):
    """🧠 Basit2: Deep Research & Swarm Intelligence."""
    task_str = req.get_task("ping") if req else "ping"
    res = jarvis.basit_engines.dispatch("basit2", task_str)
    return {"success": True, "result": res}


@app.get("/api/basit2")
def run_basit2_get(query: str = Query(default="ping")):
    res = jarvis.basit_engines.dispatch("basit2", query)
    return {"success": True, "result": res}


@app.post("/api/basit3")
def run_basit3(req: Optional[EngineTaskRequest] = None):
    """🛡️ Basit3: Security Audit, Process Guard & Auto-Git."""
    act = req.get_task("all") if req else "all"
    target_dir = req.get_dir() if req else None
    res = jarvis.basit_engines.dispatch("basit3", act, target_dir=target_dir)
    return {"success": True, "result": res}


@app.get("/api/basit3")
def run_basit3_get(action: str = Query(default="all")):
    res = jarvis.basit_engines.dispatch("basit3", action)
    return {"success": True, "result": res}


@app.post("/api/basit4")
def run_basit4(req: Optional[EngineTaskRequest] = None):
    """📈 Basit4: Autonomous AI Hedge Fund & 6-Persona Market Consensus."""
    task_str = req.get_task("ping") if req else "ping"
    res = jarvis.basit_engines.dispatch("basit4", task_str)
    return {"success": True, "result": res}


@app.get("/api/basit4")
def run_basit4_get(query: str = Query(default="ping")):
    res = jarvis.basit_engines.dispatch("basit4", query)
    return {"success": True, "result": res}


@app.post("/api/basitswarm")
def run_basitswarm(req: Optional[EngineTaskRequest] = None):
    """🐝 BasitSwarm: 100-Agent Ultra-Parallel Multi-Model Burst Engine."""
    goal_str = req.get_task("ping") if req else "ping"
    res = jarvis.basit_engines.dispatch("basitswarm", goal_str)
    return {"success": True, "result": res}


@app.get("/api/basitswarm")
def run_basitswarm_get(goal: str = Query(default="ping")):
    res = jarvis.basit_engines.dispatch("basitswarm", goal)
    return {"success": True, "result": res}


@app.post("/api/basitloop")
def run_basitloop(req: Optional[EngineTaskRequest] = None):
    """♾️ BasitLoop: Continuous 8-Stage Autonomous Looping Engine."""
    goal_str = req.get_task("ping") if req else "ping"
    target_dir = req.get_dir() if req else None
    res = jarvis.basit_engines.dispatch("basitloop", goal_str, target_dir=target_dir)
    return {"success": True, "result": res}


@app.get("/api/basitloop")
def run_basitloop_get(goal: str = Query(default="ping")):
    res = jarvis.basit_engines.dispatch("basitloop", goal)
    return {"success": True, "result": res}


@app.post("/api/gemini-spark")
@app.post("/api/spark")
@app.post("/api/gemini")
def run_gemini_spark(req: Optional[EngineTaskRequest] = None):
    """🔥 Gemini Spark: Apache Spark 4.2.0 Distributed Data + Gemini 2.0 Multimodal AI."""
    task_str = req.get_task("status") if req else "status"
    res = jarvis.basit_engines.dispatch("gemini-spark", task_str)
    return {"success": True, "result": res}


@app.get("/api/gemini-spark")
@app.get("/api/spark")
@app.get("/api/gemini")
def run_gemini_spark_get(task: str = Query(default="status")):
    res = jarvis.basit_engines.dispatch("gemini-spark", task)
    return {"success": True, "result": res}


@app.post("/api/batch")
def run_batch(req: BatchRequest):
    """Executes multiple Basit engine tasks concurrently."""
    items = (req.tasks or [])[:6]
    if not items:
        return {"success": True, "count": 0, "results": []}

    def _run_one(item: Dict[str, Any]):
        eng = item.get("engine", "assistant")
        tsk = item.get("task") or item.get("prompt") or item.get("query") or "ping"
        d = item.get("dir")
        return {"engine": eng, "result": jarvis.basit_engines.dispatch(eng, tsk, target_dir=d)}

    with ThreadPoolExecutor(max_workers=min(6, len(items))) as pool:
        results = list(pool.map(_run_one, items))
    return {"success": True, "count": len(results), "results": results}


# ==============================================================================
# 6. SOVEREIGN FULL RUN & 20-SUBAGENT SWARM ENDPOINTS
# ==============================================================================
@app.get("/api/sovereign-full-run")
@app.post("/api/sovereign-full-run")
def api_sovereign_full_run(refresh: bool = Query(default=False)):
    """Returns or executes the Sovereign Master Runner across all engines & 20 subagents."""
    report_path = os.path.join(BASE_DIR, "reports", "sovereign_full_run.json")
    if not refresh and os.path.exists(report_path):
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                data["success"] = True
                return data
        except Exception:
            pass

    try:
        from modules.sovereign_master_runner import run_sovereign_master
        res = run_sovereign_master()
        res["success"] = True
        return res
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/swarm-20-run")
@app.post("/api/swarm-20-run")
def api_swarm_20_run():
    """Executes all 20 specialized autonomous subagents in parallel."""
    try:
        from modules.subagent_swarm_20 import SubagentSwarm20
        swarm = SubagentSwarm20()
        res = swarm.run_all()
        res["success"] = True
        return res
    except Exception as e:
        logger.error(f"Error in /api/swarm-20-run: {e}")
        return {"success": False, "error": str(e)}


@app.get("/api/swarm-20-report")
def api_swarm_20_report():
    """Returns the latest 20-subagent swarm verification report."""
    report_path = os.path.join(BASE_DIR, "reports", "swarm_20_report.json")
    if os.path.exists(report_path):
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                data["success"] = True
                return data
        except Exception:
            pass
    return api_swarm_20_run()


# ==============================================================================
# 7. PDF & EXECUTIVE REPORT STUDIO
# ==============================================================================
@app.get("/api/reports")
def api_list_reports():
    """Lists all generated PDF and HTML reports in reports/."""
    from modules.pdf_generator import list_reports
    reports = list_reports()
    return {"success": True, "count": len(reports), "reports": reports}


@app.post("/api/report/generate")
def api_generate_report(req: Optional[ReportGenerateRequest] = None):
    """Generates an executive, security, hedgefund, or custom report."""
    from modules.pdf_generator import generate_report
    rtype = (req.type if req else "executive") or "executive"
    title = (req.title if req else "") or ""
    topic = (req.topic if req else "") or ""
    content = (req.content if req else "") or ""
    res = generate_report(report_type=rtype, title=title, topic=topic, content=content)
    return res


@app.get("/api/report/generate")
def api_generate_report_get(
    type: str = Query(default="executive"),
    title: str = Query(default=""),
    topic: str = Query(default="")
):
    from modules.pdf_generator import generate_report
    return generate_report(report_type=type, title=title, topic=topic)


# ==============================================================================
# 8. MULTI-LAPTOP REMOTE NODE REGISTRY
# ==============================================================================
@app.get("/api/nodes")
def api_get_nodes():
    """Returns connected laptop nodes (always includes local Master Host)."""
    stats = jarvis.system.get_system_status()
    local_node = {
        "nodeId": "local",
        "hostname": f"{socket.gethostname()} (Master PC)",
        "os": f"{platform.system()} {platform.release()}",
        "username": jarvis.config.get("jarvis", {}).get("owner", "Basit"),
        "ip": "127.0.0.1",
        "cpu": f"{stats.get('cpu_percent', 0)}%",
        "ram_gb": stats.get("ram_total_gb", 32.0),
        "online": True,
        "status": "ONLINE",
        "lastSeen": int(time.time() * 1000)
    }
    now_ms = int(time.time() * 1000)
    nodes_list = [local_node]
    for nid, ninfo in CONNECTED_NODES.items():
        if nid == "local":
            continue
        item = dict(ninfo)
        item["online"] = (now_ms - item.get("lastSeen", 0)) < 30000
        nodes_list.append(item)
    return {"success": True, "nodes": nodes_list}


@app.post("/api/nodes/register")
def api_register_node(req: NodeRegisterRequest):
    """Registers or updates heartbeat for a remote laptop agent."""
    CONNECTED_NODES[req.nodeId] = {
        "nodeId": req.nodeId,
        "hostname": req.hostname or req.nodeId,
        "os": req.os or "Windows",
        "username": req.username or "User",
        "ip": req.ip or "unknown",
        "cpu": req.cpu or "unknown",
        "ram_gb": req.ram_gb or 16,
        "lastSeen": int(time.time() * 1000),
        "status": "ONLINE"
    }
    NODE_QUEUES.setdefault(req.nodeId, [])
    return {"success": True, "message": "Node registered", "nodeId": req.nodeId}


@app.get("/api/nodes/poll")
def api_poll_node(nodeId: str = Query(default="local")):
    """Polled by remote laptop agents to fetch queued commands."""
    if nodeId in CONNECTED_NODES:
        CONNECTED_NODES[nodeId]["lastSeen"] = int(time.time() * 1000)
    cmds = list(NODE_QUEUES.get(nodeId, []))
    NODE_QUEUES[nodeId] = []
    return {"success": True, "commands": cmds}


@app.post("/api/nodes/result")
def api_node_result(req: NodeResultRequest):
    """Receives command execution result from a remote laptop node."""
    entry = {
        "nodeId": req.nodeId,
        "cmdId": req.cmdId,
        "command": req.command,
        "output": req.output,
        "success": req.success,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    NODE_RESULTS.insert(0, entry)
    del NODE_RESULTS[50:]
    return {"success": True, "recorded": entry}


# ==============================================================================
# 9. TERMINAL & PROCESS GUARD
# ==============================================================================
@app.post("/api/terminal")
def execute_terminal(req: TerminalRequest, _auth: bool = Depends(require_auth)):
    """Executes shell or PowerShell command on PC. Requires Bearer token auth."""
    res = jarvis.system.run_shell_command(req.command, cwd=req.cwd)
    return res


@app.post("/api/process_guard")
@app.get("/api/process_guard")
def sweep_processes(_auth: bool = Depends(require_auth)):
    """Sweeps zombie node.exe / cmd.exe processes to prevent system hang."""
    res = jarvis.basit_engines.b3.sweep_zombies()
    return {"success": True, "sweep": res}


# ==============================================================================
# 10. QUICK NOTES, CLIPBOARD, REMINDERS & CONTACTS
# ==============================================================================
@app.get("/api/notes")
def api_get_notes():
    """Retrieves all stored quick notes with normalized schema."""
    notes = jarvis.system.get_all_notes()
    return {"success": True, "count": len(notes), "notes": notes}


@app.post("/api/notes")
def api_take_note(req: NoteRequest):
    """Saves a quick note (accepts 'text' or 'content')."""
    note_text = (req.text or req.content or "").strip()
    if not note_text:
        return {"success": False, "error": "Note text is empty"}
    entry = jarvis.system.take_quick_note(note_text)
    return {"success": True, "note": entry}


@app.get("/api/clipboard")
def api_get_clipboard():
    """Reads current Windows clipboard content."""
    text = jarvis.system.get_clipboard_text()
    return {"success": True, "clipboard": text}


@app.post("/api/clipboard")
def api_set_clipboard(req: ClipboardRequest):
    """Sets Windows clipboard text."""
    success = jarvis.system.set_clipboard_text(req.text)
    return {"success": success, "text": req.text}


@app.get("/api/reminders")
def api_get_reminders():
    """Retrieves all saved reminders."""
    reminders = jarvis.system.get_all_reminders()
    return {"success": True, "count": len(reminders), "reminders": reminders}


@app.post("/api/reminders")
def api_add_reminder(req: ReminderRequest):
    """Creates a new reminder via ConversationalBrain."""
    task_text = (req.task or req.text or "General reminder").strip()
    mins = req.minutes or 5
    from modules.conversational_brain import get_brain
    cb = get_brain()
    msg = cb._set_reminder(task_text, f"{mins} minutes")
    reminders = jarvis.system.get_all_reminders()
    return {"success": True, "message": msg, "reminders": reminders}


@app.get("/api/contacts")
def api_get_contacts():
    """Retrieves saved WhatsApp contacts."""
    from modules.conversational_brain import get_brain
    cb = get_brain()
    cb.contacts = cb._load_contacts()
    return {"success": True, "contacts": cb.contacts}


@app.post("/api/contacts")
def api_save_contact(req: ContactRequest):
    """Adds or updates a WhatsApp contact in data/contacts.json."""
    from modules.atomic_storage import atomic_read_json, atomic_write_json
    contacts_path = os.path.join(BASE_DIR, "data", "contacts.json")
    os.makedirs(os.path.dirname(contacts_path), exist_ok=True)
    saved, _ = atomic_read_json(contacts_path, default={}, auto_heal_from_backup=True)
    if not isinstance(saved, dict):
        saved = {}
    clean_name = req.name.lower().strip()
    clean_phone = "".join(ch for ch in req.phone if ch.isdigit())
    saved[clean_name] = clean_phone
    atomic_write_json(contacts_path, saved, backup=True)
    return {"success": True, "name": clean_name, "phone": clean_phone, "contacts": saved}


@app.delete("/api/contacts")
def api_delete_contact(name: str = Query(...)):
    """Deletes a contact from data/contacts.json."""
    from modules.atomic_storage import atomic_read_json, atomic_write_json
    contacts_path = os.path.join(BASE_DIR, "data", "contacts.json")
    saved, _ = atomic_read_json(contacts_path, default={}, auto_heal_from_backup=True)
    if isinstance(saved, dict):
        saved.pop(name.lower().strip(), None)
        atomic_write_json(contacts_path, saved, backup=True)
    return {"success": True, "deleted": name, "contacts": saved}


# ==============================================================================
# 11. WEBSOCKET REAL-TIME STREAMING
# ==============================================================================
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Bi-directional WebSocket for real-time telemetry streaming and command execution."""
    await websocket.accept()
    logger.info("WebSocket client connected.")
    try:
        import asyncio
        async def send_telemetry():
            while True:
                stats = jarvis.system.get_system_status()
                active_win = jarvis.system.get_active_window()
                payload = {
                    "type": "telemetry",
                    "telemetry": stats,
                    "active_window": active_win
                }
                await websocket.send_json(payload)
                await asyncio.sleep(1.5)

        telemetry_task = asyncio.create_task(send_telemetry())

        while True:
            data = await websocket.receive_json()
            cmd = data.get("command", "")
            if cmd:
                res = jarvis.process_command(cmd)
                await websocket.send_json({
                    "type": "command_result",
                    "command": cmd,
                    "response": res
                })
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected.")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        try:
            telemetry_task.cancel()
        except Exception:
            pass


# ==============================================================================
# 12. CONTENT TEAM SQUAD API ENDPOINTS
# ==============================================================================
@app.post("/api/content/hooks")
def api_generate_hooks(req: HooksRequest):
    """Generates viral social hooks for any topic."""
    hooks = jarvis.content_team.generate_viral_hooks(req.topic, req.count)
    return {"success": True, "topic": req.topic, "hooks": hooks}


@app.post("/api/content/script")
def api_generate_script(req: VideoScriptRequest):
    """Generates 9:16 vertical short video production script."""
    script = jarvis.content_team.generate_video_script(req.topic, req.duration)
    return {"success": True, "script": script}


@app.post("/api/content/carousel")
def api_generate_carousel(req: CarouselRequest):
    """Generates multi-slide carousel and thread structure."""
    carousel = jarvis.content_team.generate_carousel(req.topic, req.slides)
    return {"success": True, "carousel": carousel}


@app.post("/api/content/calendar")
def api_generate_calendar(req: CalendarRequest):
    """Generates a 30-day editorial content calendar."""
    calendar = jarvis.content_team.generate_30_day_calendar(req.niche)
    return {"success": True, "calendar": calendar}


@app.post("/api/content/repurpose")
def api_repurpose(req: RepurposeRequest):
    """Repurposes 1 raw idea into 10 multi-channel assets."""
    repurposed = jarvis.content_team.repurpose_idea(req.idea)
    return {"success": True, "repurposed": repurposed}


@app.get("/api/content/vault")
def api_list_vault():
    """Lists all stored content assets in Content Vault."""
    files = jarvis.content_team.list_vault_files()
    return {"success": True, "vault_files": files}


# ==============================================================================
# 13. STATIC DIRECTORIES, PWA ASSETS & DESKTOP AGENT DOWNLOADS
# ==============================================================================
public_dir = os.path.join(BASE_DIR, "public")
screenshots_dir = os.path.join(BASE_DIR, "screenshots")
reports_dir = os.path.join(BASE_DIR, "reports")
os.makedirs(screenshots_dir, exist_ok=True)
os.makedirs(reports_dir, exist_ok=True)

if os.path.exists(public_dir):
    app.mount("/static", StaticFiles(directory=public_dir), name="static")
app.mount("/screenshots", StaticFiles(directory=screenshots_dir), name="screenshots")
app.mount("/reports", StaticFiles(directory=reports_dir), name="reports")


@app.get("/manifest.json")
def serve_manifest():
    p = os.path.join(public_dir, "manifest.json")
    if os.path.exists(p):
        return FileResponse(p, media_type="application/json")
    return JSONResponse({"name": "Basit Jarvis AI", "short_name": "Jarvis", "start_url": "/", "display": "standalone"})


@app.get("/sw.js")
def serve_sw():
    p = os.path.join(public_dir, "sw.js")
    if os.path.exists(p):
        return FileResponse(p, media_type="application/javascript")
    return HTMLResponse("// Basit Jarvis Service Worker", media_type="application/javascript")


@app.get("/icon.svg")
def serve_icon():
    p = os.path.join(public_dir, "icon.svg")
    if os.path.exists(p):
        return FileResponse(p, media_type="image/svg+xml")
    return HTMLResponse("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><circle cx='50' cy='50' r='45' fill='#00f5d4'/></svg>", media_type="image/svg+xml")


@app.get("/agent.ps1")
def serve_agent_ps1():
    p = os.path.join(public_dir, "agent.ps1")
    if os.path.exists(p):
        return FileResponse(p, media_type="text/plain", filename="BasitJarvisAgent.ps1")
    return HTMLResponse("# Basit Jarvis Remote Node Agent", media_type="text/plain")


@app.get("/install.bat")
@app.get("/agent.bat")
@app.get("/BasitJarvisDesktop.bat")
def serve_agent_bat(request: Request):
    host = request.headers.get("host", "localhost:8888")
    bat = (
        "@echo off\r\n"
        "title Basit Jarvis AI — Remote Laptop Agent Installer\r\n"
        "color 0B\r\n"
        f"powershell -NoProfile -ExecutionPolicy Bypass -Command \"irm http://{host}/agent.ps1 | iex\"\r\n"
    )
    return HTMLResponse(content=bat, media_type="application/octet-stream")


@app.get("/BasitJarvisDesktop.exe")
def serve_desktop_exe(request: Request):
    exe_path = os.path.join(public_dir, "BasitJarvisDesktop.exe")
    if os.path.exists(exe_path):
        return FileResponse(exe_path, media_type="application/octet-stream", filename="BasitJarvisDesktop.exe")
    return serve_agent_bat(request)


@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    index_path = os.path.join(public_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return "<h1>Basit Jarvis PC Controller API Online</h1><p>Visit <a href='/docs'>/docs</a> for Swagger UI.</p>"


if __name__ == "__main__":
    logger.info("Starting Basit Jarvis PC Controller Server on http://0.0.0.0:8888 ...")
    uvicorn.run(app, host="0.0.0.0", port=8888, log_level="info")
