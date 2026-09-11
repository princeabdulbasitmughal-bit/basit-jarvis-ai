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

# Prevent crash when running under pythonw.exe (where stdout/stderr are None)
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Setup logging to both console and file
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "server_debug.log")
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

# Enable CORS so SuperSender Pro (running on port 3000/3001) can freely call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
            
            class SafeTTS:
                def speak(self, text: str):
                    logger.info(f"[VOICE]: {text}")
            self.tts = SafeTTS()

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
                elif intent == "ai_query":
                    return self.brain.ask(cmd)
            return "Command processed."

    jarvis = FallbackJarvis()


# Request Models
class CommandRequest(BaseModel):
    command: str

class SpeakRequest(BaseModel):
    text: str

class MacroRequest(BaseModel):
    name: str

class VolumeRequest(BaseModel):
    level: int

class HooksRequest(BaseModel):
    topic: str
    count: Optional[int] = 5

class VideoScriptRequest(BaseModel):
    topic: str
    duration: Optional[int] = 45

class CarouselRequest(BaseModel):
    topic: str
    slides: Optional[int] = 6

class CalendarRequest(BaseModel):
    niche: str

class RepurposeRequest(BaseModel):
    idea: str

class Basit1Request(BaseModel):
    prompt: str
    target_dir: Optional[str] = None

class Basit2Request(BaseModel):
    query: str

class Basit3Request(BaseModel):
    action: Optional[str] = "all"

class BasitLoopRequest(BaseModel):
    goal: str
    target_dir: Optional[str] = None

class TerminalRequest(BaseModel):
    command: str
    cwd: Optional[str] = None

class NoteRequest(BaseModel):
    text: str

class ClipboardRequest(BaseModel):
    text: str


@app.get("/api/status")
def get_status():
    """Returns real-time PC health, resource utilization, and Jarvis state."""
    stats = jarvis.system.get_system_status()
    return {
        "status": "ONLINE",
        "service": "Basit Jarvis PC Controller",
        "owner": jarvis.config.get("jarvis", {}).get("owner", "Basit"),
        "telemetry": stats,
        "active_macros": list(jarvis.macros.macros.keys())
    }


@app.post("/api/command")
def execute_command(req: CommandRequest):
    """Executes any natural language or direct PC command."""
    logger.info(f"API command received: '{req.command}'")
    response_text = jarvis.process_command(req.command)
    return {
        "success": True,
        "command": req.command,
        "response": response_text
    }


@app.post("/api/speak")
def speak_text(req: SpeakRequest):
    """Speaks text out loud via PC speakers."""
    jarvis.tts.speak(req.text)
    return {"success": True, "spoken": req.text}


@app.post("/api/volume")
def set_volume(req: VolumeRequest):
    """Directly sets PC master volume (0 - 100)."""
    success = jarvis.system.set_volume(req.level)
    return {"success": success, "volume": req.level}


@app.post("/api/show_desktop")
def show_desktop():
    """Minimizes all windows to show desktop."""
    jarvis.system.minimize_all()
    return {"success": True, "action": "minimize_all"}


@app.post("/api/screenshot")
def take_screenshot():
    """Captures screenshot and returns path."""
    path = jarvis.system.take_screenshot()
    return {"success": bool(path), "path": path}


@app.get("/api/macros")
def list_macros():
    """Lists all user-defined macros."""
    return {"macros": jarvis.macros.macros}


@app.post("/api/macro")
def trigger_macro(req: MacroRequest):
    """Executes a specific macro by name."""
    success = jarvis.macros.execute_macro(req.name)
    return {"success": success, "macro": req.name}


# ------------------------------------------------------------------------------
# BASIT AUTONOMOUS POWER ENGINES & CLUSTER ENDPOINTS
# ------------------------------------------------------------------------------
@app.get("/api/cluster")
def get_cluster():
    """Returns latency and health status of all integrated AI engines."""
    status = jarvis.brain.get_cluster_status()
    return {"success": True, "cluster": status}


@app.post("/api/basit1")
def run_basit1(req: Basit1Request):
    """⚡ Basit1: Ultra-Fast Code Generation & Scaffolding."""
    res = jarvis.basit_engines.dispatch("basit1", req.prompt, target_dir=req.target_dir)
    return {"success": True, "result": res}


@app.post("/api/basit2")
def run_basit2(req: Basit2Request):
    """🧠 Basit2: Deep Research & Swarm Intelligence."""
    res = jarvis.basit_engines.dispatch("basit2", req.query)
    return {"success": True, "result": res}


@app.post("/api/basit3")
def run_basit3(req: Basit3Request):
    """🛡️ Basit3: Security Audit, Process Guard & Auto-Git."""
    res = jarvis.basit_engines.dispatch("basit3", req.action or "all")
    return {"success": True, "result": res}


@app.post("/api/basitloop")
def run_basitloop(req: BasitLoopRequest):
    """♾️ BasitLoop: Continuous 8-Stage Autonomous Looping Engine."""
    res = jarvis.basit_engines.dispatch("basitloop", req.goal, target_dir=req.target_dir)
    return {"success": True, "result": res}


@app.post("/api/terminal")
def execute_terminal(req: TerminalRequest):
    """Executes shell or PowerShell command on PC."""
    res = jarvis.system.run_shell_command(req.command, cwd=req.cwd)
    return res


@app.post("/api/process_guard")
def sweep_processes():
    """Sweeps zombie node.exe / cmd.exe processes to prevent system hang."""
    res = jarvis.basit_engines.basit3.sweep_zombies()
    return {"success": True, "sweep": res}


# ------------------------------------------------------------------------------
# QUICK NOTES, CLIPBOARD & WINDOW CONTROL ENDPOINTS
# ------------------------------------------------------------------------------
@app.get("/api/notes")
def api_get_notes():
    """Retrieves all stored quick notes."""
    notes = jarvis.system.get_all_notes()
    return {"success": True, "notes": notes}


@app.post("/api/notes")
def api_take_note(req: NoteRequest):
    """Saves a quick note."""
    entry = jarvis.system.take_quick_note(req.text)
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


# ------------------------------------------------------------------------------
# SPEAKER & VOICE OUTPUT CONTROL
# ------------------------------------------------------------------------------
@app.get("/api/speaker/status")
def api_speaker_status():
    """Returns whether TTS / Master Audio is muted."""
    tts_muted = jarvis.tts.muted if hasattr(jarvis, 'tts') else False
    sys_muted = jarvis.system.get_mute_status()
    return {"success": True, "tts_muted": tts_muted, "system_muted": sys_muted, "muted": tts_muted or sys_muted}


@app.post("/api/speaker/toggle")
def api_speaker_toggle():
    """Toggles speaker output and TTS voice on/off."""
    if hasattr(jarvis, 'tts'):
        tts_muted = jarvis.tts.toggle_mute()
    else:
        tts_muted = False
    sys_muted = jarvis.system.toggle_mute()
    return {"success": True, "tts_muted": tts_muted, "system_muted": sys_muted, "status": "MUTED" if tts_muted else "ACTIVE"}


@app.post("/api/speaker/mute")
def api_speaker_mute():
    """Mutes speaker and voice output."""
    if hasattr(jarvis, 'tts'):
        jarvis.tts.mute()
    jarvis.system.mute(True)
    return {"success": True, "status": "MUTED"}


@app.post("/api/speaker/unmute")
def api_speaker_unmute():
    """Unmutes speaker and voice output."""
    if hasattr(jarvis, 'tts'):
        jarvis.tts.unmute()
    jarvis.system.mute(False)
    return {"success": True, "status": "ACTIVE"}


# ------------------------------------------------------------------------------
# WEBSOCKET REAL-TIME STREAMING
# ------------------------------------------------------------------------------
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


# ------------------------------------------------------------------------------
# CONTENT TEAM SQUAD API ENDPOINTS
# ------------------------------------------------------------------------------
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


# Web UI Dashboard Route
public_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")
if os.path.exists(public_dir):
    app.mount("/static", StaticFiles(directory=public_dir), name="static")

@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    index_path = os.path.join(public_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return "<h1>Basit Jarvis PC Controller API Online</h1><p>Visit <a href='/docs'>/docs</a> for Swagger UI.</p>"


if __name__ == "__main__":
    logger.info("Starting Basit Jarvis PC Controller Server on http://0.0.0.0:8888 ...")
    uvicorn.run(app, host="0.0.0.0", port=8888, log_level="info")
