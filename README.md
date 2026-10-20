# 👑 Basit Jarvis AI — Sovereign PC Controller & Neural Voice Core

Basit Jarvis AI is an autonomous, voice-enabled intelligent PC assistant and sovereign local operating core powered by the 8-Engine AI Arsenal and Dual-Node GPU compute (Local NVIDIA RTX A6000 48GB + Remote NVIDIA RTX 5090 32GB).

## 🚀 Key Features

- **Neural Voice Synthesizer**: Kokoro-82M & Edge-TTS high-fidelity bilingual voice engine.
- **Bilingual NLP Core**: Seamless comprehension and execution of English and Roman Urdu voice & text commands.
- **8-Engine Sovereign Arsenal**:
  - **Basit1**: Supreme Swarm Engine / Local Qwen 2.5 Coder 32B on RTX A6000
  - **Basit2**: Claude 3.7 Thinking Suite, GraphRAG & Deep Research
  - **Basit3**: OWASP Security Auditor & Zero-Hang SRE Watchdog
  - **Basit4**: Autonomous Market Intelligence & AI Hedge Fund
  - **Gemini Spark**: Google Gemini Multimodal Reasoning Core
  - **BasitSwarm**: Ultra-Parallel Multi-Agent Swarm Orchestrator
  - **BasitLoop**: 24/7 Continuous Self-Healing & Improvement Loop
  - **Arsenal Router**: Central dynamic model dispatch
- **Desktop Automation**: Win32 COM, active window control, automated screen analysis, and process supervisory guards.
- **Persistent Memory**: SQLite WAL-mode session memory with cryptographic integrity verification.
- **OWASP Hardened**: Strict Bearer token auth, locked CORS boundaries, and secure command execution.

## 📡 REST API & Service Endpoints (Port 8888)

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/ping` | `GET` | Health check heartbeat |
| `/api/status` | `GET` | Comprehensive system health & engine matrix |
| `/api/cluster` | `GET` | Dual-Node GPU cluster telemetry |
| `/api/command` | `POST` | Natural language voice & text command dispatcher |
| `/api/engine/{name}` | `POST` | Direct dispatch to individual AI engines |
| `/api/voices` | `GET` | Catalog of available neural voice profiles |

## 🛠️ Quick Start

```powershell
# Launch Basit Jarvis AI Server
python -X utf8 server.py
```

Runs on `http://127.0.0.1:8888` under active daemon supervision.
