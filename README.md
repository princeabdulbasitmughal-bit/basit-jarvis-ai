# 👑 BASIT JARVIS AI — SOVEREIGN PC CONTROLLER & AUTONOMOUS AI OS

**Version:** 4.0.0  
**Owner:** Basit  
**Location:** `E:\basit-jarvis-ai`  
**API Port:** `http://localhost:8888`  
**AI Compute:** Dual-Node GPU Cluster (RTX A6000 + RTX 5090) + Groq 120B + Mistral Codestral + Hugging Face 15-Token Pool  

---

## 🌟 Overview

**Basit Jarvis AI** is a sovereign, standalone desktop AI operating layer designed to grant **complete, hands-free voice and programmatic control over Windows PC**. It operates both as a real-time bilingual (Urdu + English) voice assistant and as a high-performance REST/WebSocket server for external platforms, featuring native execution of the **Basit Autonomous Power Engines** (`/basit1`, `/basit2`, `/basit3`, `/basitloop`).

---

## ⚡ 3 Ways to Run

### 1. 🚀 One-Click Master Launcher (`start_all.bat`)
Starts everything at once:
1. Starts background REST API & Web Server on port `8888`
2. Opens the Cyberpunk Glassmorphism Web Dashboard (`http://localhost:8888`)
3. Starts the Voice Assistant listening for *"Hey Jarvis"* or *"Basit"*!

```bash
# Double click start_all.bat or run:
E:\basit-jarvis-ai\start_all.bat
```

### 2. 🎙️ Voice-Only Mode (`start_voice.bat`)
Listens to microphone with silence detection and bilingual acoustic parsing:
- Wake words: *"Hey Jarvis"*, *"Basit"*
- Hotkey fallback: `Ctrl + Shift + J`

### 3. 🌐 API & Web Dashboard Mode (`start_server.bat`)
Runs FastAPI server on port `8888` with interactive cyberpunk web controls.
- Web HUD: `http://localhost:8888`
- Swagger API Docs: `http://localhost:8888/docs`

---

## 👑 The Basit Autonomous Power Suite (/basit1, /basit2, /basit3, /basitloop)

Jarvis can execute these engines directly from voice, text, web HUD, or API:

| Engine | Voice Triggers | Functionality | Primary Engine |
|---|---|---|---|
| **⚡ `/basit1`** | *"Basit 1 ..."*, *"Code generator ..."*, *"Code karo ..."* | Instant sub-second code generation, scaffolding, bug fixing | Groq 120B / Codestral / Qwen 32B |
| **🧠 `/basit2`** | *"Basit 2 ..."*, *"Deep research ..."*, *"Research karo ..."* | Multi-source web research, Claude extended reasoning, consensus swarms | Claude 3.5 Sonnet / Kimi K3 |
| **🛡️ `/basit3`** | *"Basit 3 ..."*, *"Security check ..."*, *"Sweep zombies ..."* | OWASP security auditing, zero-hang process guard, auto-git | Local Guardian Agent |
| **♾️ `/basitloop`** | *"Basit loop ..."*, *"Start loop ..."*, *"Autonomous mode ..."* | Continuous 8-stage loop (Plan ➔ Build ➔ Fix ➔ Deploy) | Multi-Model Consensus |

---

## ⚡ Multi-Tier AI Compute Cluster

| Tier | Engine / Hardware | Specialty | Latency |
|---|---|---|---|
| **Tier 1** | **Groq LPU** (`llama-3.3-70b-versatile` / `gpt-oss-120b`) | Instant voice reasoning & logic | **0.8s** |
| **Tier 2** | **Mistral Cloud** (`codestral-latest`) | Production Python/TypeScript code generation | **1.4s** |
| **Tier 3** | **Local RTX A6000 (48GB VRAM)** | Local Ollama (`qwen2.5-coder:32b`, `qwen3`) | **Local ($0)** |
| **Tier 4** | **Remote RTX 5090 Cluster** | Moonshot Kimi K3 (1M-context window) | **Cluster** |
| **Tier 5** | **Hugging Face 15-Token Pool** | Serverless failover across 15 accounts | **Zero-limit pool** |
| **Tier 6** | **Anthropic Claude & OpenAI** | Claude 3.5 Sonnet & GPT-4o deep review | **Frontier** |

---

## 🎙️ Bilingual Voice Commands (Urdu & English)

### 🖥️ Windows & Apps
- `"Chrome kholo"` / `"Open Chrome"`
- `"VS Code band karo"` / `"Close VS Code"`
- `"Desktop dikhao"` / `"Show desktop"` (Win + D)
- `"Window minimize kardo"` / `"Maximize window"`
- `"Window band karo"` (Alt + F4)

### 🔊 Audio & Brightness
- `"Awaz 80 kardo"` / `"Set volume to 80%"`
- `"Awaz barhao"` / `"Volume up"`
- `"Awaz kam karo"` / `"Volume down"`
- `"Awaz band kardo"` / `"Mute volume"`
- `"Awaz kholo"` / `"Unmute volume"`
- `"Roshni 70 kardo"` / `"Set brightness to 70%"`

### 📁 Files, Folders & Explorer
- `"Downloads folder kholo"` / `"Open downloads"`
- `"Desktop folder kholo"` / `"Documents kholo"`
- `"E drive open karo"` / `"C drive kholo"`
- `"File report.pdf dhoondo"` / `"Search file financial in desktop"`

### 💻 Terminal & Git
- `"Git status check karo"`
- `"Terminal mein chalao Write-Output 'Hello'"`
- `"Run in powershell: dir"`

### 🔒 Security & Power
- `"Screenshot lo"` / `"Take a screenshot"`
- `"PC lock kardo"` / `"Lock computer"`
- `"Sleep kardo"` / `"Put PC to sleep"`
- `"Shutdown kardo"` (requires confirmation)
- `"System status batao"` (CPU, RAM, Disk, Battery)

---

## 🛠️ REST API Reference (Port 8888)

| Method | Route | Payload | Description |
|---|---|---|---|
| `POST` | `/api/command` | `{"command": "chrome kholo"}` | Executes any bilingual or slash command |
| `POST` | `/api/basit1` | `{"prompt": "write a fastapi server"}` | ⚡ Instant code generation & scaffolding |
| `POST` | `/api/basit2` | `{"query": "frontier AI models"}` | 🧠 Deep research and synthesis |
| `POST` | `/api/basit3` | `{"action": "all"}` | 🛡️ Security audit and process sweep |
| `POST` | `/api/basitloop` | `{"goal": "optimize project"}` | ♾️ 8-Stage autonomous looping engine |
| `POST` | `/api/content/hooks` | `{"topic": "AI SaaS", "count": 5}` | 🎨 Generates 5 viral copywriting hooks |
| `POST` | `/api/content/script` | `{"topic": "Automation", "duration": 45}` | 🎬 9:16 Video script (Reels/TikTok/Shorts) |
| `POST` | `/api/content/carousel`| `{"topic": "Growth Hacks", "slides": 7}` | 📑 LinkedIn/IG carousel slide blueprint |
| `POST` | `/api/content/calendar`| `{"niche": "E-Commerce", "month": "Sep"}` | 📅 30-Day cross-platform editorial calendar |
| `POST` | `/api/content/repurpose`| `{"idea": "Omnichannel"}` | 🔄 1-to-10 multi-format omnichannel repurposer |
| `GET`  | `/api/content/vault`   | — | 📂 Lists all saved campaign assets in vault |
| `POST` | `/api/terminal` | `{"command": "Get-Process"}` | Safe shell/PowerShell execution |
| `POST` | `/api/process_guard`| `{}` | Sweeps orphaned zombie node processes |
| `GET`  | `/api/cluster` | — | Telemetry & latency for all AI cluster nodes |
| `POST` | `/api/speak` | `{"text": "Hello Basit"}` | Voice synthesis via PC speakers |
| `POST` | `/api/volume` | `{"level": 75}` | Sets master volume (0-100%) |
| `POST` | `/api/screenshot` | — | Captures screenshot and returns path |
| `GET`  | `/api/status` | — | Real-time CPU, RAM, Disk telemetry |
| `GET`  | `/` | — | Cyberpunk Glassmorphism Web Control HUD |

---

## 🎨 Autonomous AI Content Studio (6-Agent Squad)

Basit Jarvis AI includes a sovereign 6-agent marketing & content creation powerhouse:
1. **HookMaster**: 5 Viral psychological hooks (Contrarian, Curiosity Gap, Negative Warning, Hormozi Value).
2. **ShortsDirector**: Scene-by-scene 9:16 Vertical Video Production Script with camera cues, voiceover, and b-roll.
3. **CarouselGenius**: Multi-slide LinkedIn / Instagram Carousels & Twitter/X viral threads.
4. **RepurposePro**: Converts 1 core concept into 10 multi-channel marketing assets.
5. **CalendarStrategist**: 30-day cross-platform editorial calendar with daily themes and peak posting times.
6. **ExportManager & Vault**: Automatically saves all generated assets to `content_vault/`.

### Content Voice Triggers:
- *"Hey Jarvis, generate 5 viral hooks for WhatsApp Marketing"*
- *"Hey Jarvis, write a 45 second TikTok script about SuperSender Pro"*
- *"Hey Jarvis, create a 30 day content calendar for Ecommerce"*
- *"Hey Jarvis, repurpose this idea into 10 formats"*

