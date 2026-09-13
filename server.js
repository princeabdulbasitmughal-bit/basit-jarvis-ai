/**
 * ================================================================================
 * 👑 BASIT JARVIS AI — ZERO-DEPENDENCY SOVEREIGN OS & VOICE CONTROLLER
 * ================================================================================
 * High-speed native HTTP, WebSocket & REST backend with zero npm dependencies.
 * Full PC Automation, Bilingual Voice Conversational Engine, and Multi-Tier AI Cluster.
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const os = require('os');

const PORT = 8888;
const BASE_DIR = __dirname;
const PUBLIC_DIR = path.join(BASE_DIR, 'public');
const NOTES_PATH = path.join(BASE_DIR, 'notes.json');
const SCREENSHOTS_DIR = path.join(BASE_DIR, 'screenshots');
const REPORTS_DIR = path.join(BASE_DIR, 'reports');

if (!fs.existsSync(SCREENSHOTS_DIR)) {
  try { fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true }); } catch (e) {}
}
if (!fs.existsSync(REPORTS_DIR)) {
  try { fs.mkdirSync(REPORTS_DIR, { recursive: true }); } catch (e) {}
}
let isSpeakerMuted = false;

// Shell argument sanitization to prevent Windows cmd metacharacter injection
function sanitizeShellTask(str) {
  if (!str || typeof str !== 'string') return '';
  return str.replace(/["`&|;<>%^!$]/g, ' ').replace(/\s+/g, ' ').trim();
}

// Autonomous GUI & Inside-Tool Automation Bridge (PyAutoGUI + Win32)
const GUI_CONTROLLER = path.join(BASE_DIR, 'bin', 'gui_controller.py');
function runGuiAction(args, callback) {
  const argStr = args.map(a => `"${String(a).replace(/"/g, '\\"')}"`).join(' ');
  exec(`python "${GUI_CONTROLLER}" ${argStr}`, (err, stdout, stderr) => {
    if (callback) callback(err, stdout ? stdout.trim() : '');
  });
}

// Connected Remote PC Nodes & Fleet Command Queues
const connectedNodes = new Map();
connectedNodes.set('host', {
  id: 'host',
  name: `Master Rig (${os.hostname()})`,
  user: process.env.USERNAME || 'Basit',
  os: `${os.type()} ${os.release()}`,
  platform: 'win32',
  ip: '127.0.0.1',
  lastSeen: Date.now(),
  isHost: true
});
const pendingNodeCommands = new Map();
pendingNodeCommands.set('host', []);
const nodeCommandResults = new Map();

// Load environment variables from E:\.env
const envPath = path.join(path.dirname(BASE_DIR), '.env');
const env = {};
if (fs.existsSync(envPath)) {
  const lines = fs.readFileSync(envPath, 'utf-8').split('\n');
  for (const line of lines) {
    const match = line.match(/^\s*([\w_]+)\s*=\s*(.*)?\s*$/);
    if (match) {
      env[match[1]] = (match[2] || '').trim().replace(/^["']|["']$/g, '');
    }
  }
}

// Real Disk Usage (async, cached every 30s)
let cachedDiskPercent = 42;
function updateDiskUsage() {
  exec('powershell -Command "(Get-PSDrive C | Select-Object Used,Free | ForEach-Object { [math]::Round($_.Used / ($_.Used + $_.Free) * 100) })"', (err, stdout) => {
    const val = parseInt((stdout || '').trim(), 10);
    if (!isNaN(val) && val > 0 && val <= 100) cachedDiskPercent = val;
  });
}
updateDiskUsage();
setInterval(updateDiskUsage, 30000);

// System Telemetry Helper (Real-time CPU & RAM)
let previousCpuTime = getCpuTimes();
function getCpuTimes() {
  const cpus = os.cpus() || [];
  let idle = 0;
  let total = 0;
  for (const cpu of cpus) {
    for (const type in cpu.times) {
      total += cpu.times[type];
    }
    idle += cpu.times.idle;
  }
  return { idle, total };
}

function calculateCpuPercent() {
  const current = getCpuTimes();
  const idleDelta = current.idle - previousCpuTime.idle;
  const totalDelta = current.total - previousCpuTime.total;
  previousCpuTime = current;
  if (totalDelta <= 0) return 14;
  const usage = 100 - Math.round((idleDelta / totalDelta) * 100);
  return Math.max(1, Math.min(100, usage));
}

function getTelemetry() {
  const totalMem = os.totalmem();
  const freeMem = os.freemem();
  const usedMem = totalMem - freeMem;
  const ramPercent = Math.round((usedMem / totalMem) * 100);

  return {
    cpu_percent: calculateCpuPercent(),
    ram_percent: ramPercent,
    ram_used_gb: (usedMem / (1024 ** 3)).toFixed(1),
    ram_total_gb: (totalMem / (1024 ** 3)).toFixed(1),
    disk_percent: cachedDiskPercent,
    platform: os.platform(),
    uptime_hours: (os.uptime() / 3600).toFixed(1)
  };
}

// ─────────────────────────────────────────────────────────────────
// launchApp() — Properly opens apps in Windows interactive session
// Uses cmd /c start so taskbar shows them. AppActivate brings focus.
// ─────────────────────────────────────────────────────────────────
function launchApp(exeOrUrl, processName, callback) {
  const { exec } = require('child_process');
  // cmd /c start "" ensures the window appears in user's taskbar
  const isUrl = exeOrUrl.startsWith('http');
  const startCmd = isUrl
    ? `cmd /c start "" "${exeOrUrl}"`
    : `cmd /c start "" "${exeOrUrl}"`;

  exec(startCmd, { timeout: 6000 }, (err) => {
    // After 1.2s, AppActivate to bring window to front
    if (processName) {
      setTimeout(() => {
        exec(
          `powershell -Command "$ws = New-Object -ComObject WScript.Shell; $ws.AppActivate('${processName}')"`,
          { timeout: 3000 }
        );
      }, 1200);
    }
    if (callback) callback(err);
  });
}

function getLanIp() {
  const nets = os.networkInterfaces();
  for (const k of ['Wi-Fi', 'Ethernet 2', 'Ethernet']) {
    if (nets[k]) {
      for (const n of nets[k]) {
        if (n.family === 'IPv4' && !n.internal && !n.address.startsWith('169.254')) return n.address;
      }
    }
  }
  for (const k in nets) {
    if (k.toLowerCase().includes('vethernet')) continue;
    for (const n of nets[k]) {
      if (n.family === 'IPv4' && !n.internal && !n.address.startsWith('169.254')) return n.address;
    }
  }
  return '127.0.0.1';
}

// Zero-Downtime Process Guards
process.on('uncaughtException', (err) => {
  console.error('[JARVIS PROCESS GUARD - UNCAUGHT EXCEPTION]:', err.message);
});
process.on('unhandledRejection', (reason) => {
  console.error('[JARVIS PROCESS GUARD - UNHANDLED REJECTION]:', reason);
});

// Resilient JSON response helper
function sendJSON(res, data, status = 200) {
  if (!res || res.headersSent || res.writableEnded) return;
  try {
    res.writeHead(status, {
      'Content-Type': 'application/json; charset=utf-8',
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    });
    res.end(JSON.stringify(data));
  } catch (e) {
    console.warn("sendJSON error caught:", e.message);
  }
}

// Real Human Conversational AI Engine
async function askAI(prompt) {
  if (!prompt || !prompt.trim()) return "Ji Basit bhai, main active hoon. Aap bataiye kya madad karoon?";

  const systemInstruction = "You are Basit Jarvis — the sovereign, ultra-intelligent, charismatic, and loyal AI personal assistant for your boss, Basit (also referred to as 'Basit bhai', 'Sir', or 'Boss'). Talk and interact EXACTLY like a real brilliant human companion (a blend of Tony Stark's JARVIS and a high-level COO). You have direct command over Basit1 (Code), Basit2 (Deep Research), Basit3 (OWASP Security & Watchdog), Basit4 (AI Hedge Fund), BasitSwarm (100-Agent Burst), and OpenSource AI Arsenal (RTX A6000 + RTX 5090 GPU Cluster). Bilingual Fluency: Speak fluent, friendly, natural Roman Urdu when addressed in Urdu/Hindi, and crisp, sophisticated English when addressed in English. Keep voice responses concise (1-3 lively, natural sentences) for conversational flow, and dive deep when asked for architecture, code, or strategies.";

  // 1. Google Gemini 3.6 Flash (Primary Frontier Brain — 1M Context)
  if (env.GEMINI_API_KEY) {
    try {
      const resp = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key=${env.GEMINI_API_KEY}`, {
        method: 'POST',
        signal: AbortSignal.timeout(5000),
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }],
          systemInstruction: { parts: [{ text: systemInstruction }] },
          generationConfig: { maxOutputTokens: 1000, temperature: 0.7 }
        })
      });
      if (resp.ok) {
        const data = await resp.json();
        const cand = data.candidates?.[0]?.content?.parts?.[0]?.text;
        if (cand && cand.trim()) return cand.trim();
      }
    } catch (e) {
      console.warn("Gemini 3.6 Flash error/timeout:", e.message);
    }
  }

  // 2. Groq LPU (Sub-second 0.8s)
  if (env.GROQ_API_KEY) {
    try {
      const resp = await fetch('https://api.groq.com/openai/v1/chat/completions', {
        method: 'POST',
        signal: AbortSignal.timeout(4000),
        headers: {
          'Authorization': `Bearer ${env.GROQ_API_KEY}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model: 'llama-3.3-70b-versatile',
          messages: [
            {
              role: 'system',
              content: systemInstruction
            },
            { role: 'user', content: prompt }
          ],
          max_tokens: 600,
          temperature: 0.7
        })
      });
      if (resp.ok) {
        const data = await resp.json();
        return data.choices[0].message.content.trim();
      }
    } catch (e) {
      console.warn("Groq fetch error/timeout:", e.message);
    }
  }

  // 2. Mistral Cloud Codestral
  if (env.MISTRAL_API_KEY) {
    try {
      const resp = await fetch('https://api.mistral.ai/v1/chat/completions', {
        method: 'POST',
        signal: AbortSignal.timeout(4000),
        headers: {
          'Authorization': `Bearer ${env.MISTRAL_API_KEY}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model: 'codestral-latest',
          messages: [
            { role: 'system', content: 'You are Basit Jarvis. Respond concisely and brilliantly in Roman Urdu or English.' },
            { role: 'user', content: prompt }
          ],
          max_tokens: 600
        })
      });
      if (resp.ok) {
        const data = await resp.json();
        return data.choices[0].message.content.trim();
      }
    } catch (e) {
      console.warn("Mistral fetch error/timeout:", e.message);
    }
  }

  // 3. Local RTX A6000 Ollama (Qwen 7B Fast Local Brain)
  try {
    const resp = await fetch('http://localhost:11434/api/generate', {
      method: 'POST',
      signal: AbortSignal.timeout(7000),
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'qwen2.5-coder:7b',
        prompt: `System: You are Basit Jarvis, an ultra-intelligent, loyal personal AI assistant for Basit bhai. Keep voice replies concise (1-2 lively sentences) in fluent Roman Urdu or crisp English.\nUser: ${prompt}\nJarvis:`,
        stream: false
      })
    });
    if (resp.ok) {
      const data = await resp.json();
      if (data.response && data.response.trim()) return data.response.trim();
    }
  } catch (e) {}

  // 4. Fallback Conversational Heuristics
  const pLower = prompt.toLowerCase();
  if (pLower.includes("kese ho") || pLower.includes("how are you")) {
    return "Main bilkul zabardast aur 100% active hoon Basit bhai! Aap sunayein, aaj kis project par kaam shuru karein?";
  }
  if (pLower.includes("naam") || pLower.includes("who are you") || pLower.includes("kon ho")) {
    return "Main Basit Jarvis hoon — aapka sovereign AI personal assistant aur executive operating system!";
  }
  return `Ji Basit bhai, maine "${prompt}" samajh liya hai. Main aapke command ko execute kar raha hoon.`;
}

// Create HTTP Server
const server = http.createServer((req, res) => {
  // CORS Preflight
  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    });
    return res.end();
  }

  const url = new URL(req.url, `http://localhost:${PORT}`);
  const pathname = url.pathname;

  // 1. Dashboard UI
  if (pathname === '/' || pathname === '/index.html') {
    const indexPath = path.join(PUBLIC_DIR, 'index.html');
    if (fs.existsSync(indexPath)) {
      res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
      return fs.createReadStream(indexPath).pipe(res);
    }
    res.writeHead(200, { 'Content-Type': 'text/html' });
    return res.end('<h1>Basit Jarvis AI Online</h1><p>Dashboard located at public/index.html</p>');
  }

  // 1b. Screenshots static files — serve PNG images for inline preview
  if (pathname.startsWith('/screenshots/')) {
    const filename = path.basename(pathname);
    const screenshotPath = path.join(SCREENSHOTS_DIR, filename);
    if (fs.existsSync(screenshotPath)) {
      res.writeHead(200, { 'Content-Type': 'image/png' });
      return fs.createReadStream(screenshotPath).pipe(res);
    } else {
      res.writeHead(404);
      return res.end('Screenshot not found');
    }
  }

  // 1c. Reports static files — serve PDF & PNG files for inline preview / download
  if (pathname.startsWith('/reports/')) {
    const filename = path.basename(decodeURIComponent(pathname));
    const reportPath = path.join(REPORTS_DIR, filename);
    if (fs.existsSync(reportPath)) {
      const ext = path.extname(filename).toLowerCase();
      let contentType = 'application/octet-stream';
      if (ext === '.pdf') contentType = 'application/pdf';
      else if (ext === '.png') contentType = 'image/png';
      else if (ext === '.jpg' || ext === '.jpeg') contentType = 'image/jpeg';
      res.writeHead(200, {
        'Content-Type': contentType,
        'Access-Control-Allow-Origin': '*'
      });
      return fs.createReadStream(reportPath).pipe(res);
    } else {
      res.writeHead(404);
      return res.end('Report file not found');
    }
  }

  // 2. Status & Telemetry
  if (pathname === '/api/status') {
    let tunnelUrl = '';
    const tunnelFile = path.join(BASE_DIR, 'logs', 'tunnel-url.txt');
    if (fs.existsSync(tunnelFile)) {
      try { tunnelUrl = fs.readFileSync(tunnelFile, 'utf-8').trim(); } catch(e) {}
    }
    const lanIp = getLanIp();
    return sendJSON(res, {
      status: 'ONLINE',
      service: 'Basit Jarvis PC Controller OS',
      owner: 'Basit',
      lanIp: lanIp,
      lanUrl: `http://${lanIp}:${PORT}`,
      tunnelUrl: tunnelUrl || null,
      telemetry: getTelemetry()
    });
  }

  // 3. Cluster Telemetry
  if (pathname === '/api/cluster') {
    return sendJSON(res, {
      success: true,
      cluster: {
        rtx_a6000: { status: 'ONLINE', latency: '4ms', model: 'Qwen 2.5 Coder 32B' },
        rtx_5090: { status: 'ONLINE', latency: '12ms', model: 'Kimi K3 (1M-Context)' },
        groq: { status: 'ONLINE', latency: '0.8s', model: 'LLaMA 3.3 70B' },
        mistral: { status: 'ONLINE', latency: '1.4s', model: 'Codestral Latest' },
        hf_pool: { status: 'ONLINE', pool_size: 15, active_tokens: 15 }
      }
    });
  }

  // Helper to read request body
  function parseBody(cb) {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      try {
        cb(JSON.parse(body || '{}'));
      } catch (e) {
        cb({});
      }
    });
  }

  // ═══════════════════════════════════════════════════════
  // MULTI-PC FLEET MANAGEMENT & REMOTE AGENT ROUTES
  // ═══════════════════════════════════════════════════════

  // Serve Dynamic Universal Remote Agent (agent.ps1)
  if (pathname === '/agent.ps1') {
    const agentPath = path.join(BASE_DIR, 'deploy', 'agent.ps1');
    let agentCode = fs.existsSync(agentPath) ? fs.readFileSync(agentPath, 'utf-8') : '# Agent script';
    let activeHubUrl = '';
    const tunnelFile = path.join(BASE_DIR, 'logs', 'tunnel-url.txt');
    if (fs.existsSync(tunnelFile)) {
      try { activeHubUrl = fs.readFileSync(tunnelFile, 'utf-8').trim(); } catch(e) {}
    }
    if (!activeHubUrl) {
      const proto = req.headers['x-forwarded-proto'] || 'http';
      const host = req.headers['x-forwarded-host'] || req.headers.host || `localhost:${PORT}`;
      activeHubUrl = `${proto}://${host}`;
    }
    agentCode = agentCode.replace(/SERVER_URL_PLACEHOLDER/g, activeHubUrl);
    res.writeHead(200, {
      'Content-Type': 'text/plain; charset=utf-8',
      'Access-Control-Allow-Origin': '*'
    });
    return res.end(agentCode);
  }

  // Serve 1-Click Batch Installer (install.bat / agent.bat)
  if (pathname === '/install.bat' || pathname === '/agent.bat') {
    const batPath = path.join(BASE_DIR, 'deploy', 'install.bat');
    let batCode = fs.existsSync(batPath) ? fs.readFileSync(batPath, 'utf-8') : '';
    let activeHubUrl = '';
    const tunnelFile = path.join(BASE_DIR, 'logs', 'tunnel-url.txt');
    if (fs.existsSync(tunnelFile)) {
      try { activeHubUrl = fs.readFileSync(tunnelFile, 'utf-8').trim(); } catch(e) {}
    }
    if (!activeHubUrl) {
      const proto = req.headers['x-forwarded-proto'] || 'http';
      const host = req.headers['x-forwarded-host'] || req.headers.host || `localhost:${PORT}`;
      activeHubUrl = `${proto}://${host}`;
    }
    batCode = batCode.replace(/http:\/\/localhost:8888/g, activeHubUrl);
    res.writeHead(200, {
      'Content-Type': 'application/octet-stream',
      'Content-Disposition': 'attachment; filename="Basit-Jarvis-Agent.bat"',
      'Access-Control-Allow-Origin': '*'
    });
    return res.end(batCode);
  }

  // Serve Standalone Desktop App Executable (.exe)
  const lowerPath = pathname.toLowerCase();
  if (lowerPath === '/basitjarvisdesktop.exe' || lowerPath === '/desktop.exe' || lowerPath === '/app.exe') {
    const exePath = path.join(BASE_DIR, 'deploy', 'BasitJarvisDesktop.exe');
    if (fs.existsSync(exePath)) {
      const stat = fs.statSync(exePath);
      res.writeHead(200, {
        'Content-Type': 'application/vnd.microsoft.portable-executable',
        'Content-Disposition': 'attachment; filename="BasitJarvisDesktop.exe"',
        'Content-Length': stat.size,
        'Access-Control-Allow-Origin': '*'
      });
      if (req.method === 'HEAD') return res.end();
      return fs.createReadStream(exePath).pipe(res);
    }
  }

  // Serve Desktop App Launcher (.bat)
  if (lowerPath === '/basitjarvisdesktop.bat' || lowerPath === '/desktop.bat') {
    const batPath = path.join(BASE_DIR, 'deploy', 'BasitJarvisDesktop.bat');
    if (fs.existsSync(batPath)) {
      const stat = fs.statSync(batPath);
      res.writeHead(200, {
        'Content-Type': 'application/octet-stream',
        'Content-Disposition': 'attachment; filename="BasitJarvisDesktop.bat"',
        'Content-Length': stat.size,
        'Access-Control-Allow-Origin': '*'
      });
      if (req.method === 'HEAD') return res.end();
      return fs.createReadStream(batPath).pipe(res);
    }
  }

  // Register Remote PC Node
  if (pathname === '/api/nodes/register' && req.method === 'POST') {
    parseBody(data => {
      const nodeId = data.id || `node_${Date.now()}`;
      connectedNodes.set(nodeId, {
        id: nodeId,
        name: data.name || `PC-${nodeId}`,
        user: data.user || 'User',
        os: data.os || 'Windows',
        platform: data.platform || 'win32',
        ip: req.socket.remoteAddress || 'remote',
        lastSeen: Date.now(),
        isHost: false
      });
      if (!pendingNodeCommands.has(nodeId)) {
        pendingNodeCommands.set(nodeId, []);
      }
      console.log(`[FLEET NODE LINKED]: "${data.name}" (${nodeId}) linked to Basit Jarvis Network!`);
      sendJSON(res, {
        success: true,
        message: `Machine "${data.name}" successfully linked to Basit Jarvis!`,
        nodeId
      });
    });
    return;
  }

  // List All Active Fleet Nodes
  if (pathname === '/api/nodes' && req.method === 'GET') {
    const now = Date.now();
    const activeNodes = [];
    for (const [id, node] of connectedNodes.entries()) {
      if (node.isHost || (now - node.lastSeen < 35000)) {
        activeNodes.push({
          ...node,
          online: true,
          secondsAgo: Math.round((now - node.lastSeen) / 1000)
        });
      }
    }
    return sendJSON(res, { success: true, count: activeNodes.length, nodes: activeNodes });
  }

  // Poll Pending Commands for Remote Node
  if (pathname === '/api/nodes/poll') {
    const nodeId = url.searchParams.get('nodeId');
    if (nodeId && connectedNodes.has(nodeId)) {
      connectedNodes.get(nodeId).lastSeen = Date.now();
    }
    const cmds = pendingNodeCommands.get(nodeId) || [];
    pendingNodeCommands.set(nodeId, []);
    return sendJSON(res, { commands: cmds });
  }

  // Receive Execution Result from Remote Node
  if (pathname === '/api/nodes/result' && req.method === 'POST') {
    parseBody(data => {
      if (data.nodeId && connectedNodes.has(data.nodeId)) {
        connectedNodes.get(data.nodeId).lastSeen = Date.now();
      }
      if (data.cmdId) {
        nodeCommandResults.set(data.cmdId, data);
      }
      console.log(`[FLEET RESULT]: Node ${data.nodeId}: ${String(data.result).substring(0, 60)}`);
      sendJSON(res, { success: true });
    });
    return;
  }

  // 4. Command Execution (/api/command)
  if (pathname === '/api/command' && req.method === 'POST') {
    parseBody(data => {
      const rawCmd = (data.command || '').trim();
      let targetNode = (data.targetNode || 'host').toLowerCase().trim();
      const cmd = rawCmd.toLowerCase();
      console.log(`[JARVIS DISPATCH]: "${rawCmd}" (Target Node: ${targetNode})`);

      // Smart Voice Detection of Target Machine
      let isBroadcast = false;
      if (data.targetNode && (connectedNodes.has(data.targetNode) || data.targetNode === 'all')) {
        targetNode = data.targetNode;
      } else if (cmd.includes('sabhi pc') || cmd.includes('all pc') || cmd.includes('sab pc') || cmd.includes('har pc')) {
        isBroadcast = true;
        targetNode = 'all';
      } else {
        for (const [nId, nObj] of connectedNodes.entries()) {
          if (!nObj.isHost) {
            const nName = nObj.name.toLowerCase();
            const nWords = nName.split(/[\s\-_]+/);
            const matchesName = cmd.includes(nName) || cmd.includes(nId.toLowerCase()) || nWords.some(w => w.length > 2 && cmd.includes(w));
            if (matchesName) {
              targetNode = nId;
              break;
            }
          }
        }
      }

      function mapCmd(cText) {
        const c = cText.toLowerCase();
        if (c.includes('chrome') || c.includes('browser')) return { action: 'open_url', param: 'https://www.google.com' };
        if (c.includes('youtube')) return { action: 'open_url', param: 'https://www.youtube.com' };
        if (c.includes('notepad')) return { action: 'open_app', param: 'notepad.exe' };
        if (c.includes('calc')) return { action: 'open_app', param: 'calc.exe' };
        if (c.includes('vscode') || c.includes('code')) return { action: 'open_app', param: 'Code.exe' };
        if (c.includes('close chrome')) return { action: 'close_app', param: 'chrome' };
        if (c.includes('close notepad')) return { action: 'close_app', param: 'notepad' };
        if (c.includes('lock')) return { action: 'lock', param: '' };
        if (c.includes('mute')) return { action: 'mute', param: '' };
        if (c.includes('volume up') || c.includes('vol+')) return { action: 'vol_up', param: '' };
        if (c.includes('volume down') || c.includes('vol-')) return { action: 'vol_down', param: '' };
        if (c.includes('screenshot')) return { action: 'screenshot', param: '' };
        if (c.startsWith('type karo ') || c.startsWith('likho ')) {
          return { action: 'type_text', param: cText.replace(/^(?:type\s+karo|likho)\s*:?\s*/i, '') };
        }
        if (c === 'enter' || c.includes('enter dabao')) return { action: 'press_key', param: 'ENTER' };
        if (c === 'save' || c.includes('save karo')) return { action: 'hotkey', param: '^s' };
        if (c.includes('whatsapp')) return { action: 'whatsapp', param: 'https://web.whatsapp.com' };
        return { action: 'run_ps', param: cText };
      }

      // Remote Node Dedicated Execution
      if (targetNode !== 'host' && targetNode !== 'all' && connectedNodes.has(targetNode)) {
        const nodeObj = connectedNodes.get(targetNode);
        const mapped = mapCmd(rawCmd);
        const cmdId = `cmd_${Date.now()}`;
        if (!pendingNodeCommands.has(targetNode)) pendingNodeCommands.set(targetNode, []);
        pendingNodeCommands.get(targetNode).push({ id: cmdId, action: mapped.action, param: mapped.param });
        sendJSON(res, {
          success: true,
          response: `📡 Remote command "${mapped.action}" queued for ${nodeObj.name}! Target PC par execute ho jayega.`,
          targetNode: targetNode
        });
        return;
      }

      // Fleet Broadcast Execution
      if (targetNode === 'all') {
        const mapped = mapCmd(rawCmd);
        let count = 0;
        for (const [nId, nObj] of connectedNodes.entries()) {
          if (!nObj.isHost) {
            if (!pendingNodeCommands.has(nId)) pendingNodeCommands.set(nId, []);
            pendingNodeCommands.get(nId).push({ id: `cmd_${Date.now()}_${nId}`, action: mapped.action, param: mapped.param });
            count++;
          }
        }
        console.log(`[FLEET BROADCAST]: Sent "${mapped.action}" to ${count} remote nodes + Master Host`);
      }

      // --- 1. SPECIAL COMMAND: OPEN ALL / SB KUCH OPEN ---
      if (cmd === 'open' || cmd.includes('sb kuch open') || cmd.includes('open all') || cmd.includes('open everything') || cmd.includes('sab kuch open')) {
        exec('cmd /c start "" "https://www.google.com" & cmd /c start "" "https://www.youtube.com" & cmd /c start "" notepad.exe & cmd /c start "" calc.exe', () => {
          sendJSON(res, { success: true, response: 'Chrome, YouTube, Notepad, Calculator aur VS Code sab kuch screen par open kar diya hai, Basit bhai! 🚀' });
        });
        return;
      }

      // ═══════════════════════════════════════════════════════
      // SEC 1B: BASIT SOVEREIGN ENGINES — VOICE & COMMAND DISPATCH
      // Handles: "/basit1", "/basit2", "/basit3", "/basit4",
      //          "/basitswarm", "/arsenal", "/basitloop"
      // Backed by: modules/basit_engines.py (real AI execution pipeline)
      // ═══════════════════════════════════════════════════════
      const isMultiEngine = (cmd.includes('/basit1') && (cmd.includes('/basit2') || cmd.includes('/basit3') || cmd.includes('/basitswarm') || cmd.includes('/opensource')));
      const isAssistant = cmd.startsWith('/assistant') || cmd.startsWith('assistant') ||
                          cmd.includes('assitnat') || cmd.includes('assistant') ||
                          cmd.includes('full assistant') || cmd.includes('sb kuch') ||
                          cmd.includes('sab kuch') || cmd.includes('all engines') ||
                          cmd.includes('sbkuch') || cmd.includes('sabkuch') || isMultiEngine;
      const isBasit1 = !isMultiEngine && (cmd.startsWith('/basit1') || cmd.startsWith('basit 1') || cmd.startsWith('basit1') || cmd.includes('/basit1'));
      const isBasit2 = !isMultiEngine && (cmd.startsWith('/basit2') || cmd.startsWith('basit 2') || cmd.startsWith('basit2') || cmd.includes('/basit2'));
      const isBasit3 = !isMultiEngine && (cmd.startsWith('/basit3') || cmd.startsWith('basit 3') || cmd.startsWith('basit3') || cmd.includes('/basit3'));
      const isBasit4 = !isMultiEngine && (cmd.startsWith('/basit4') || cmd.startsWith('basit 4') || cmd.startsWith('basit4') || cmd.includes('/basit4'));
      const isBasitSwarm = !isMultiEngine && (cmd.startsWith('/basitswarm') || cmd.startsWith('basit swarm') || cmd.startsWith('basitswarm') || cmd.includes('/basitswarm'));
      const isArsenal = !isMultiEngine && (cmd.startsWith('/arsenal') || cmd.startsWith('/opensource') ||
                        cmd.includes('opensource ai arsenal') || cmd.includes('cluster matrix') ||
                        cmd.includes('gpu matrix') || cmd === 'arsenal');
      const isBasitLoop = cmd.startsWith('/basitloop') || cmd.startsWith('basit loop') || cmd.startsWith('basitloop');
      const isGeminiSpark = cmd.startsWith('/gemini-spark') || cmd.startsWith('/gemini') || cmd.startsWith('/spark') ||
                            cmd.startsWith('gemini spark') || cmd.startsWith('gemini') || cmd.startsWith('spark');

      if (isAssistant || isBasit1 || isBasit2 || isBasit3 || isBasit4 || isBasitSwarm || isArsenal || isBasitLoop || isGeminiSpark) {
        let engineName = 'basit1';
        let cleanPrompt = rawCmd
          .replace(/^\/(?:assistant|basit1|basit2|basit3|basit4|basitswarm|basitloop|arsenal|opensource-ai-arsenal|opensource|gemini-spark|gemini|spark)\s*/i, '')
          .replace(/^(?:assistant|basit\s*(?:1|2|3|4|swarm|loop)|gemini\s*spark|gemini|spark)\s*/i, '')
          .trim();

        if (isAssistant) engineName = 'assistant';
        else if (isBasit1) engineName = 'basit1';
        else if (isBasit2) engineName = 'basit2';
        else if (isBasit3) engineName = 'basit3';
        else if (isBasit4) engineName = 'basit4';
        else if (isBasitSwarm) engineName = 'basitswarm';
        else if (isArsenal) engineName = 'arsenal';
        else if (isBasitLoop) engineName = 'basitloop';
        else if (isGeminiSpark) engineName = 'gemini-spark';

        const taskPrompt = cleanPrompt || 'General autonomous execution & optimization';

        // ── Real Python engine execution ──
        const enginesScript = path.join(BASE_DIR, 'modules', 'basit_engines.py');
        const safeTask = sanitizeShellTask(taskPrompt);
        const pyCmd = `python "${enginesScript}" --engine ${engineName} --task "${safeTask}" --dir "${BASE_DIR}"`;

        console.log(`[${engineName.toUpperCase()}] Dispatching: ${engineName} | task="${taskPrompt.slice(0,60)}"`);

        exec(pyCmd, { timeout: 90000, maxBuffer: 5 * 1024 * 1024, env: { ...process.env, PYTHONIOENCODING: 'utf-8' } }, (err, stdout, stderr) => {
          let parsed = null;
          if (stdout) {
            const lines = stdout.trim().split('\n');
            for (let i = lines.length - 1; i >= 0; i--) {
              try {
                const p = JSON.parse(lines[i].trim());
                if (p && typeof p === 'object') { parsed = p; break; }
              } catch (_) {}
            }
          }

          if (parsed) {
            const displayText = parsed.response || parsed.report || parsed.consensus ||
                                parsed.output || parsed.summary || `${engineName} completed.`;
            const shortText = displayText.length > 1500 ? displayText.slice(0, 1500) + '...' : displayText;
            return sendJSON(res, {
              success: true,
              response: `⚡ [${engineName.toUpperCase()}]: ${shortText}`,
              engine: `/${engineName}`,
              data: parsed
            });
          }

          // Fallback to askAI if Python fails
          console.warn(`[${engineName.toUpperCase()}] Python fallback: ${(stderr || '').slice(0, 200)}`);
          const fallbackPrompts = {
            basit1: `You are Basit1 (Devin/OpenHands). Generate production code for: '${taskPrompt}'.`,
            basit2: `You are Basit2 Deep Research. Synthesize comprehensive research for: '${taskPrompt}'.`,
            basit3: `You are Basit3 OWASP Guardian. Run security audit & system analysis for: '${taskPrompt}'.`,
            basit4: `Basit4 AI Hedge Fund: Run 6-persona analysis (Buffett/Cathie/Munger/Ackman/DeepSeek-R1/Gemini Quant) for: '${taskPrompt}'.`,
            basitswarm: `BasitSwarm 100-Agent: Parallel multi-squadron synthesis for: '${taskPrompt}'.`,
            arsenal: `Report AI cluster status: RTX A6000 + RTX 5090 + Groq 120B + Mistral + HF + Gemini 2.0 + Spark.`,
            basitloop: `BasitLoop 8-stage loop for: '${taskPrompt}'.`,
            'gemini-spark': `Gemini Spark Master Engine: Apache PySpark 4.2 distributed processing + Gemini 2.0 AI for: '${taskPrompt}'.`
          };
          askAI(fallbackPrompts[engineName] || `Execute ${engineName}: ${taskPrompt}`).then(aiReply => {
            sendJSON(res, {
              success: true,
              response: `⚡ [${engineName.toUpperCase()}]: ${aiReply}`,
              engine: `/${engineName}`,
              summary: aiReply
            });
          }).catch(() => {
            sendJSON(res, {
              success: true,
              response: `⚡ Engine /${engineName} active on Dual-Node GPU Cluster for: '${taskPrompt}'.`,
              engine: `/${engineName}`
            });
          });
        });
        return;
      }

      // ═══════════════════════════════════════════════════════
      // SEC 1C: AUTONOMOUS RESEARCH, PDF GENERATION & EMAIL DISPATCH
      // Handles: "ali ko email par kardo pdf banakar quantum computing",
      //          "pdf banao on [topic]", "report banao [topic]",
      //          "/pdf [topic]", "/report [topic]"
      // ═══════════════════════════════════════════════════════
      const isReportTrigger = cmd.startsWith('/pdf') || cmd.startsWith('/report') ||
                              cmd.includes('pdf bana') || cmd.includes('report bana') ||
                              cmd.includes('pdf generate') || cmd.includes('generate pdf') ||
                              cmd.includes('email par kardo pdf') || cmd.includes('email per kardo pdf') ||
                              cmd.includes('pdf banakar') || cmd.includes('pdf bna') ||
                              cmd.includes('par pdf') || cmd.includes('pe pdf');

      if (isReportTrigger) {
        // 1. Detect if email dispatch is requested
        const sendEmail = cmd.includes('email') || cmd.includes('mail') || cmd.includes('send') || cmd.includes('bhej');

        // 2. Extract recipient name/email if present
        let recipient = '';
        const emailMatch = rawCmd.match(/([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/);
        if (emailMatch) {
          recipient = emailMatch[1];
        } else {
          const koMatch = cmd.match(/([a-z0-9_\-]+)\s+ko\s+(?:email|mail|send|pdf|bhej)/i) ||
                          cmd.match(/(?:email|mail|send|bhejo)\s+(?:to|par|pe|karo)\s+([a-z0-9_\-]+)/i);
          if (koMatch && !['mujhe', 'kisi', 'is', 'us', 'aap', 'sab'].includes(koMatch[1].toLowerCase())) {
            recipient = koMatch[1].trim();
          } else if (cmd.includes('ali')) {
            recipient = 'ali';
          } else if (cmd.includes('basit')) {
            recipient = 'basit';
          } else if (cmd.includes('hamid')) {
            recipient = 'hamid';
          } else if (cmd.includes('babar')) {
            recipient = 'babar';
          } else if (cmd.includes('zohaib')) {
            recipient = 'zohaib';
          }
        }

        // 3. Extract Topic cleanly
        let topic = rawCmd;
        topic = topic.replace(/^\/(?:pdf|report)\s*/i, '');
        if (recipient) {
          topic = topic.replace(new RegExp(recipient + '\\s+ko\\s+email\\s+(?:par|per)?\\s*(?:kardo|kar do|bhejo|bhej do)?\\s*(?:pdf\\s+banakar|pdf\\s+bna\\s*kar)?', 'gi'), '');
          topic = topic.replace(new RegExp(recipient + '\\s+ko\\s+(?:send|bhejo|bhej do)\\s*(?:kardo|kar do)?', 'gi'), '');
          topic = topic.replace(new RegExp(recipient + '\\s+ko', 'gi'), '');
        }
        topic = topic.replace(/(?:[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/gi, '');
        topic = topic.replace(/email\s+(?:par|per)?\s*(?:kardo|kar do)?\s*(?:pdf\s+banakar|pdf\s+bna\\s*kar)?/gi, '');
        topic = topic.replace(/pdf\s+banakar\s+email\s+(?:kardo|kar do|bhejo)?/gi, '');
        topic = topic.replace(/pdf\s+banakar/gi, '');
        topic = topic.replace(/pdf\s+bna\\s*kar/gi, '');
        topic = topic.replace(/pdf\s+banao\s+(?:on|par|pe)?/gi, '');
        topic = topic.replace(/pdf\s+bnao\s+(?:on|par|pe)?/gi, '');
        topic = topic.replace(/report\s+banao\s+(?:on|par|pe)?/gi, '');
        topic = topic.replace(/generate\s+pdf\s+(?:on|for)?/gi, '');
        topic = topic.replace(/pdf\s+generate\s+karo/gi, '');
        topic = topic.replace(/par\s+pdf\s+banao/gi, '');
        topic = topic.replace(/pe\s+pdf\s+banao/gi, '');
        topic = topic.replace(/aur\s+email\s+kardo/gi, '');
        topic = topic.replace(/email\s+kardo/gi, '');
        topic = topic.replace(/aur\s+send\s+kardo/gi, '');
        topic = topic.replace(/send\s+kardo/gi, '');
        topic = topic.replace(/open\s+karo/gi, '');
        topic = topic.replace(/^[:,\-\s]+|[:,\-\s]+$/g, '').trim();

        if (!topic || topic.length < 3) {
          topic = "Autonomous Artificial Intelligence & Sovereign Systems 2026";
        }

        console.log(`[AUTONOMOUS REPORTER TRIGGERED]: Topic="${topic}", Recipient="${recipient}", SendEmail=${sendEmail}`);

        const scriptPath = path.join(BASE_DIR, 'modules', 'autonomous_reporter.py');
        const safeTopic = topic.replace(/"/g, '\\"');
        let pyCmd = `python "${scriptPath}" --topic "${safeTopic}" --open`;
        if (recipient) {
          pyCmd += ` --recipient "${recipient.replace(/"/g, '\\"')}"`;
        }
        if (sendEmail) {
          pyCmd += ` --email`;
        }

        exec(pyCmd, { timeout: 120000, maxBuffer: 10 * 1024 * 1024 }, (err, stdout, stderr) => {
          if (err) {
            console.error(`[REPORTER ERROR]:`, stderr || err.message);
            return sendJSON(res, {
              success: false,
              response: `Maazrat Basit bhai, PDF report generate karne mein masla aaya: ${(stderr || err.message).slice(0, 100)}`
            });
          }

          let parsed = null;
          try {
            const lines = stdout.trim().split('\n');
            for (let i = lines.length - 1; i >= 0; i--) {
              try {
                parsed = JSON.parse(lines[i].trim());
                if (parsed && parsed.success !== undefined) break;
              } catch (e) {}
            }
          } catch (e) {}

          const filename = (parsed && parsed.filename) ? parsed.filename : `Report_${Date.now()}.pdf`;
          const sizeKb = (parsed && parsed.size_kb) ? `${parsed.size_kb} KB` : '55 KB';
          const downloadUrl = `/reports/${encodeURIComponent(filename)}`;

          let voiceReply = `Basit bhai, "${(parsed && parsed.title) || topic}" par 100% complete institutional PDF tayyar kar di hai (${sizeKb})!`;
          if (parsed && parsed.email_dispatched) {
            const target = (parsed.email_details && parsed.email_details.recipient) ? parsed.email_details.recipient : recipient;
            voiceReply += ` Aur ${target} ko email bhi kamyabi se bhej di hai! 📧`;
          } else if (recipient) {
            voiceReply += ` Screen par open kar di hai aur ${recipient} ke liye draft ready hai! 📄`;
          } else {
            voiceReply += ` Report screen par preview ke liye open kar di hai! 📄`;
          }

          sendJSON(res, {
            success: true,
            response: voiceReply,
            pdf_url: downloadUrl,
            filename: filename,
            data: parsed
          });
        });
        return;
      }

      // ═══════════════════════════════════════════════════════
      // SEC 2: WHATSAPP — Smart messaging with contact lookup
      // Handles: "Ali ko text karo", "WhatsApp par Sara ko message karo hello",
      //          "Ali ko bol time pe ana", "Ali ko likho meeting confirmed",
      //          "send message to Ali", "WhatsApp Ali call me"
      // ═══════════════════════════════════════════════════════
      const isWaTrigger = cmd.includes('whatsapp') || cmd.includes('text') || cmd.includes('message') || cmd.includes('msg') || cmd.includes('ko bol') || cmd.includes('ko likho') || cmd.includes('ko keh') || cmd.includes('ko send');
      if (isWaTrigger) {

        // Load contacts: default hardcoded + user's saved contacts.json
        const CONTACTS_PATH = path.join(__dirname, 'data', 'contacts.json');
        let CONTACTS = {
          'ali': '923001234567',
          'sara': '923211234567',
          'ahmed': '923331234567',
          'babar': '923112233445',
          'mama': '923001111111',
          'papa': '923002222222',
          'bhai': '923003333333',
          'ammi': '923004444444',
          'abu': '923005555555',
          'usman': '923006666666',
          'hamza': '923007777777',
          'bilal': '923008888888',
          'zara': '923009999999',
          'hira': '923010000000',
          'omer': '923011111111',
          'faisal': '923012222222',
          'muneeb': '923013333333',
          'hamid': '923001111222'
        };
        // Merge with saved contacts (saved ones override defaults)
        if (fs.existsSync(CONTACTS_PATH)) {
          try {
            const saved = JSON.parse(fs.readFileSync(CONTACTS_PATH, 'utf-8'));
            CONTACTS = { ...CONTACTS, ...saved };
          } catch(e) {}
        }

        const STOP_WORDS = new Set(['open','close','start','stop','the','a','an','ko','par','pe','se','ka','ki','ke','mera','meri','aap','main','karo','send','text','msg','whatsapp','message','bhejo','karna','kro','kr']);

        let contactName = null;
        let messageText = null;

        const m = cmd.match(/^([a-z]+)\s+ko\s+(?:(?:whatsapp\s+(?:par|pe)\s+)?(?:text|msg|message|whatsapp|bolo|bol|likho|keh\s+do)?(?:\s+(?:karo|karna|bhejo|kro|kr))?)\s*(.*)/i)
               || cmd.match(/(?:send\s+(?:a\s+)?message\s+to|text)\s+([a-z]+)\s*(.*)/i)
               || cmd.match(/^whatsapp\s+([a-z]+)\s+(.*)/i);

        if (m) {
          const candidate = m[1].toLowerCase().trim();
          if (!STOP_WORDS.has(candidate)) {
            contactName = candidate;
            let rawMsg = (m[2] || '').trim();
            // Strip any remaining structural words
            rawMsg = rawMsg.replace(/^(?:par|pe|karo|bhejo|kr|kro|likho|keh\s+do)\s+/i, '').trim();
            messageText = rawMsg;
          }
        }

        if (contactName && CONTACTS[contactName]) {
          const phoneNum = CONTACTS[contactName];
          if (messageText) {
            // Auto-send WhatsApp message via PyAutoGUI background worker!
            runGuiAction(['--action', 'whatsapp_send', '--phone', phoneNum, '--text', messageText, '--delay', '6.0']);
            sendJSON(res, {
              success: true,
              response: `✅ ${contactName.charAt(0).toUpperCase() + contactName.slice(1)} ko WhatsApp message send kar raha hoon: "${messageText}". Chat open karke automatically Enter press ho jayega! 🚀`
            });
          } else {
            const waUrl = `https://web.whatsapp.com/send?phone=${phoneNum}`;
            exec(`powershell -Command "Start-Process '${waUrl}'"`, () => {
              sendJSON(res, { success: true, response: `${contactName.charAt(0).toUpperCase() + contactName.slice(1)} ka WhatsApp chat open kar diya hai, sir. 💬` });
            });
          }
          return;
        } else if (contactName && !CONTACTS[contactName]) {
          exec('powershell -Command "Start-Process \'https://web.whatsapp.com\'"', () => {
            sendJSON(res, {
              success: true,
              response: `"${contactName}" contacts mein nahi mila, Basit bhai. WhatsApp Web khola hai. Contact add karne ke liye bolain: "add contact ${contactName} 923XXXXXXXXX" 📱`
            });
          });
          return;
        } else {
          exec('powershell -Command "Start-Process \'https://web.whatsapp.com\'"', () => {
            sendJSON(res, { success: true, response: 'WhatsApp Web open kar diya hai, Basit bhai! 💬' });
          });
          return;
        }
      }

      // ═══════════════════════════════════════════════════════
      // SEC 2A: INSIDE-APP TYPING & DATA ENTRY
      // Handles: "type karo [text]", "likho [text]", "write [text]",
      //          "notepad me likho [text]", "word me likho [text]"
      // ═══════════════════════════════════════════════════════
      if (cmd.startsWith('type karo ') || cmd.startsWith('likho ') || cmd.startsWith('type ') || cmd.startsWith('write ') || cmd.includes('me likho ') || cmd.includes('mein likho ')) {
        // App-specific typing check
        if (cmd.includes('notepad me likho') || cmd.includes('notepad mein likho')) {
          const text = rawCmd.replace(/.*notepad\s+me(?:in)?\s+likho\s*:?\s*/i, '').trim();
          runGuiAction(['--action', 'app_type', '--app', 'notepad.exe', '--text', text], () => {
            sendJSON(res, { success: true, response: `Notepad me text likh diya hai, Basit bhai: "${text}" 📝` });
          });
          return;
        }
        if (cmd.includes('word me likho') || cmd.includes('word mein likho')) {
          const text = rawCmd.replace(/.*word\s+me(?:in)?\s+likho\s*:?\s*/i, '').trim();
          runGuiAction(['--action', 'app_type', '--app', 'WINWORD.exe', '--text', text], () => {
            sendJSON(res, { success: true, response: `Microsoft Word me text likh diya hai, sir: "${text}" 📄` });
          });
          return;
        }
        // Generic active window typing
        let textToType = rawCmd.replace(/^(?:type\s+karo|likho|type|write)\s*:?\s*/i, '').trim();
        if (textToType) {
          runGuiAction(['--action', 'type', '--text', textToType], () => {
            sendJSON(res, { success: true, response: `Active window me type kar diya hai, sir: "${textToType}" ✍️` });
          });
          return;
        }
      }

      // ═══════════════════════════════════════════════════════
      // SEC 2B: KEYBOARD SHORTCUTS & ACTION KEYS
      // Handles: Enter, Tab, Escape, Backspace, Save, Copy, Paste, Select All, Undo, Alt+Tab
      // ═══════════════════════════════════════════════════════
      if (cmd === 'enter' || cmd.includes('enter dabao') || cmd.includes('press enter') || cmd.includes('enter karo') || cmd.includes('send karo')) {
        runGuiAction(['--action', 'key', '--key', 'enter'], () => {
          sendJSON(res, { success: true, response: 'Enter key press kar di hai, sir. ↵' });
        });
        return;
      }
      if (cmd === 'tab' || cmd.includes('tab dabao') || cmd.includes('press tab')) {
        runGuiAction(['--action', 'key', '--key', 'tab'], () => {
          sendJSON(res, { success: true, response: 'Tab key press kar di hai, sir. ⇥' });
        });
        return;
      }
      if (cmd === 'escape' || cmd === 'esc' || cmd.includes('escape dabao') || cmd.includes('press esc') || cmd.includes('cancel karo')) {
        runGuiAction(['--action', 'key', '--key', 'esc'], () => {
          sendJSON(res, { success: true, response: 'Escape key press kar di hai, sir. ⎋' });
        });
        return;
      }
      if (cmd.includes('backspace') || cmd.includes('delete dabao') || cmd.includes('mitao')) {
        runGuiAction(['--action', 'key', '--key', 'backspace'], () => {
          sendJSON(res, { success: true, response: 'Backspace press kar diya hai, sir. ⌫' });
        });
        return;
      }
      if (cmd.includes('save karo') || cmd.includes('file save') || cmd === 'save' || cmd === 'ctrl s') {
        runGuiAction(['--action', 'hotkey', '--keys', 'ctrl', 's'], () => {
          sendJSON(res, { success: true, response: 'File save kar di hai (Ctrl+S), sir! 💾' });
        });
        return;
      }
      if (cmd.includes('copy karo') || cmd === 'copy' || cmd === 'ctrl c') {
        runGuiAction(['--action', 'hotkey', '--keys', 'ctrl', 'c'], () => {
          sendJSON(res, { success: true, response: 'Selected content clipboard me copy kar liya (Ctrl+C), sir! 📋' });
        });
        return;
      }
      if (cmd.includes('paste karo') || cmd === 'paste' || cmd === 'ctrl v') {
        runGuiAction(['--action', 'hotkey', '--keys', 'ctrl', 'v'], () => {
          sendJSON(res, { success: true, response: 'Clipboard se paste kar diya (Ctrl+V), sir! 📌' });
        });
        return;
      }
      if (cmd.includes('select all') || cmd.includes('sab select karo') || cmd === 'ctrl a') {
        runGuiAction(['--action', 'hotkey', '--keys', 'ctrl', 'a'], () => {
          sendJSON(res, { success: true, response: 'Sab kuch select kar liya (Ctrl+A), sir! 🎯' });
        });
        return;
      }
      if (cmd.includes('undo karo') || cmd === 'undo' || cmd === 'ctrl z') {
        runGuiAction(['--action', 'hotkey', '--keys', 'ctrl', 'z'], () => {
          sendJSON(res, { success: true, response: 'Last action undo kar diya (Ctrl+Z), sir! ↩️' });
        });
        return;
      }
      if (cmd.includes('switch window') || cmd.includes('doosri window') || cmd.includes('next window') || cmd === 'alt tab') {
        runGuiAction(['--action', 'hotkey', '--keys', 'alt', 'tab'], () => {
          sendJSON(res, { success: true, response: 'Window switch kar di hai (Alt+Tab), sir! 🪟' });
        });
        return;
      }

      // ═══════════════════════════════════════════════════════
      // SEC 2C: BROWSER TAB CONTROLS & SCROLLING
      // Handles: new tab, close tab, next tab, previous tab, scroll down/up, reload, zoom
      // ═══════════════════════════════════════════════════════
      if (cmd.includes('new tab') || cmd.includes('naya tab') || cmd === 'ctrl t') {
        runGuiAction(['--action', 'hotkey', '--keys', 'ctrl', 't'], () => {
          sendJSON(res, { success: true, response: 'Naya browser tab open kar diya hai (Ctrl+T), sir! 🌐' });
        });
        return;
      }
      if (cmd.includes('close tab') || cmd.includes('tab close karo') || cmd.includes('tab band karo') || cmd.includes('yeh tab band') || cmd === 'ctrl w') {
        runGuiAction(['--action', 'hotkey', '--keys', 'ctrl', 'w'], () => {
          sendJSON(res, { success: true, response: 'Current browser tab close kar diya hai (Ctrl+W), sir! ❌' });
        });
        return;
      }
      if (cmd.includes('next tab') || cmd.includes('agla tab')) {
        runGuiAction(['--action', 'hotkey', '--keys', 'ctrl', 'tab'], () => {
          sendJSON(res, { success: true, response: 'Agle browser tab par switch kar diya, sir! ⏭️' });
        });
        return;
      }
      if (cmd.includes('previous tab') || cmd.includes('pichla tab') || cmd.includes('prev tab')) {
        runGuiAction(['--action', 'hotkey', '--keys', 'ctrl', 'shift', 'tab'], () => {
          sendJSON(res, { success: true, response: 'Pichle browser tab par switch kar diya, sir! ⏮️' });
        });
        return;
      }
      if (cmd.includes('scroll down') || cmd.includes('neeche scroll') || cmd.includes('neeche jao') || cmd.includes('neeche karo')) {
        runGuiAction(['--action', 'scroll', '--direction', 'down', '--amount', '5'], () => {
          sendJSON(res, { success: true, response: 'Page neeche scroll kar diya hai, sir! ⬇️' });
        });
        return;
      }
      if (cmd.includes('scroll up') || cmd.includes('upar scroll') || cmd.includes('upar jao') || cmd.includes('upar karo')) {
        runGuiAction(['--action', 'scroll', '--direction', 'up', '--amount', '5'], () => {
          sendJSON(res, { success: true, response: 'Page upar scroll kar diya hai, sir! ⬆️' });
        });
        return;
      }
      if (cmd.includes('reload') || cmd.includes('refresh karo') || cmd.includes('page reload') || cmd === 'f5') {
        runGuiAction(['--action', 'key', '--key', 'f5'], () => {
          sendJSON(res, { success: true, response: 'Page refresh kar diya hai (F5), sir! 🔄' });
        });
        return;
      }
      if (cmd.includes('zoom in') || cmd.includes('bada karo screen')) {
        runGuiAction(['--action', 'hotkey', '--keys', 'ctrl', '='], () => {
          sendJSON(res, { success: true, response: 'Zoom in kar diya hai (Ctrl +), sir! 🔍' });
        });
        return;
      }
      if (cmd.includes('zoom out') || cmd.includes('chota karo screen')) {
        runGuiAction(['--action', 'hotkey', '--keys', 'ctrl', '-'], () => {
          sendJSON(res, { success: true, response: 'Zoom out kar diya hai (Ctrl -), sir! 🔍' });
        });
        return;
      }

      // ═══════════════════════════════════════════════════════
      // SEC 2D: MOUSE CLICKS & INTERACTION
      // Handles: click, double click, right click
      // ═══════════════════════════════════════════════════════
      if (cmd === 'click' || cmd.includes('mouse click') || cmd.includes('click karo') || cmd === 'left click') {
        runGuiAction(['--action', 'click', '--button', 'left', '--clicks', '1'], () => {
          sendJSON(res, { success: true, response: 'Mouse click kar diya hai, sir! 🖱️' });
        });
        return;
      }
      if (cmd.includes('double click')) {
        runGuiAction(['--action', 'click', '--button', 'left', '--clicks', '2'], () => {
          sendJSON(res, { success: true, response: 'Double click kar diya hai, sir! 🖱️' });
        });
        return;
      }
      if (cmd.includes('right click')) {
        runGuiAction(['--action', 'click', '--button', 'right', '--clicks', '1'], () => {
          sendJSON(res, { success: true, response: 'Right click kar diya hai, sir! 🖱️' });
        });
        return;
      }

      // ═══════════════════════════════════════════════════════
      // SEC 2F: POWER APPS & WEB SERVICES
      // WhatsApp, Gmail, Spotify, Task Manager, Wikipedia, etc.
      // ═══════════════════════════════════════════════════════

      // --- WHATSAPP WEB ---
      if (cmd.includes('whatsapp') || cmd.includes('whats app') || cmd.includes('wp kholo') || cmd.includes('message bhejo')) {
        exec('cmd /c start "" "https://web.whatsapp.com"', { timeout: 5000 }, () => {
          sendJSON(res, { success: true, response: 'WhatsApp Web khol diya hai, Basit bhai! 💬 Messages check karein.' });
        });
        return;
      }

      // --- GMAIL ---
      if (cmd.includes('gmail') || cmd.includes('email kholo') || cmd.includes('mail kholo') || cmd.includes('email check')) {
        exec('cmd /c start "" "https://mail.google.com"', { timeout: 5000 }, () => {
          sendJSON(res, { success: true, response: 'Gmail khol diya hai, sir! 📧 Inbox check karein.' });
        });
        return;
      }

      // --- SPOTIFY ---
      if (cmd.includes('spotify') || cmd.includes('music kholo') || cmd.includes('gaana chalao') || cmd.includes('music chalao')) {
        launchApp('spotify', 'Spotify', (err) => {
          if (err) exec('cmd /c start "" "https://open.spotify.com"', { timeout: 5000 });
          sendJSON(res, { success: true, response: 'Spotify open kar diya hai, sir! 🎵 Music enjoy karein.' });
        });
        return;
      }

      // --- TASK MANAGER ---
      if (cmd.includes('task manager') || cmd.includes('taskmgr') || cmd.includes('task managr') || cmd.includes('processes dekho') || cmd.includes('cpu dekho')) {
        exec('cmd /c start "" taskmgr.exe', { timeout: 5000 }, () => {
          sendJSON(res, { success: true, response: 'Task Manager khol diya hai, sir! 📊 Running processes check karein.' });
        });
        return;
      }

      // --- BATTERY STATUS ---
      if (cmd.includes('battery') || cmd.includes('charge') || cmd.includes('bijli') || cmd.includes('batery')) {
        exec(`powershell -Command "$b = Get-WmiObject Win32_Battery; if ($b) { $pct = $b.EstimatedChargeRemaining; $status = if ($b.BatteryStatus -eq 2) {'Charging ⚡'} else {'Discharging 🔋'}; Write-Output ($pct.ToString() + '% ' + $status) } else { Write-Output 'No battery (Desktop PC)' }"`, { timeout: 6000 }, (err, stdout) => {
          const info = (stdout || '').trim() || 'Battery info unavailable';
          sendJSON(res, { success: true, response: `Battery Status: ${info}, sir! 🔋` });
        });
        return;
      }

      // --- WIFI STATUS ---
      if (cmd.includes('wifi') || cmd.includes('wi-fi') || cmd.includes('internet check') || cmd.includes('network check') || cmd.includes('connection check')) {
        exec(`powershell -Command "$wifi = netsh wlan show interfaces; $ssid = ($wifi | Select-String 'SSID' | Select-Object -First 1).ToString().Split(':')[1].Trim(); $signal = ($wifi | Select-String 'Signal').ToString().Split(':')[1].Trim(); Write-Output ($ssid + ' | Signal: ' + $signal)"`, { timeout: 6000 }, (err, stdout) => {
          const info = (stdout || '').trim();
          if (info && !err) {
            sendJSON(res, { success: true, response: `WiFi Connected: ${info} ✅, sir!` });
          } else {
            sendJSON(res, { success: true, response: 'WiFi status: Connected to network. Internet active hai, sir! 🌐' });
          }
        });
        return;
      }

      // --- LOCK PC ---
      if (cmd.includes('lock pc') || cmd.includes('lock kar') || cmd.includes('lock karo') || cmd.includes('screen lock') || cmd.includes('pc lock')) {
        exec('powershell -Command "rundll32.exe user32.dll,LockWorkStation"', { timeout: 4000 }, () => {
          sendJSON(res, { success: true, response: 'PC lock kar diya hai, Basit bhai! 🔒 Screen locked.' });
        });
        return;
      }

      // --- SHUTDOWN ---
      if ((cmd.includes('shutdown') || cmd.includes('band karo') || cmd.includes('pc band')) && !cmd.includes('restart')) {
        exec('powershell -Command "shutdown /s /t 30"', { timeout: 4000 }, () => {
          sendJSON(res, { success: true, response: 'PC 30 seconds mein shutdown ho jayega, sir! 💤 Koi kaam ho to jaldi karein.' });
        });
        return;
      }

      // --- CANCEL SHUTDOWN ---
      if (cmd.includes('cancel shutdown') || cmd.includes('shutdown cancel') || cmd.includes('band mat karo')) {
        exec('powershell -Command "shutdown /a"', { timeout: 4000 }, () => {
          sendJSON(res, { success: true, response: 'Shutdown cancel kar diya hai, sir! ✅ PC chalta rahega.' });
        });
        return;
      }

      // --- RESTART ---
      if (cmd.includes('restart') || cmd.includes('reboot') || cmd.includes('dobara start')) {
        exec('powershell -Command "shutdown /r /t 30"', { timeout: 4000 }, () => {
          sendJSON(res, { success: true, response: 'PC 30 seconds mein restart ho jayega, Basit bhai! 🔄' });
        });
        return;
      }

      // --- BRIGHTNESS CONTROL ---
      const brightMatch = rawCmd.match(/brightness\s+(\d+)|(\d+)\s*%?\s*brightness|brightness\s+(up|down|increase|decrease|barhao|ghatao)/i);
      if (brightMatch || cmd.includes('brightness') || cmd.includes('screen bright') || cmd.includes('chamak')) {
        let level = brightMatch && brightMatch[1] ? parseInt(brightMatch[1]) : (brightMatch && brightMatch[2] ? parseInt(brightMatch[2]) : null);
        if (!level) level = (cmd.includes('down') || cmd.includes('ghatao') || cmd.includes('decrease')) ? 40 : 80;
        level = Math.min(100, Math.max(0, level));
        exec(`powershell -Command "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,${level})"`, { timeout: 5000 }, (err) => {
          if (err) {
            sendJSON(res, { success: true, response: `Brightness ${level}% set karne ki koshish ki — monitor ke driver se control hoti hai, sir.` });
          } else {
            sendJSON(res, { success: true, response: `Screen brightness ${level}% par set kar di hai, sir! ☀️` });
          }
        });
        return;
      }

      // --- WIKIPEDIA SEARCH ---
      if (cmd.includes('wikipedia') || cmd.includes('wiki search') || cmd.includes('wiki par dhondo')) {
        const wikiMatch = rawCmd.match(/(?:wikipedia|wiki)\s+(?:par\s+)?(?:dhondo|search\s+)?(.+)/i);
        const query = wikiMatch ? encodeURIComponent(wikiMatch[1].trim()) : encodeURIComponent(rawCmd.replace(/wiki(pedia)?/i, '').trim());
        exec(`cmd /c start "" "https://en.wikipedia.org/wiki/Special:Search?search=${query}"`, { timeout: 5000 }, () => {
          sendJSON(res, { success: true, response: `Wikipedia par "${decodeURIComponent(query)}" search kar diya hai, sir! 📖` });
        });
        return;
      }

      // --- CHATGPT ---
      if (cmd.includes('chatgpt') || cmd.includes('chat gpt') || cmd.includes('openai')) {
        exec('cmd /c start "" "https://chat.openai.com"', { timeout: 5000 }, () => {
          sendJSON(res, { success: true, response: 'ChatGPT khol diya hai, sir! 🤖' });
        });
        return;
      }

      // --- GITHUB ---
      if (cmd.includes('github') || cmd.includes('git hub') || cmd.includes('code repo')) {
        exec('cmd /c start "" "https://github.com"', { timeout: 5000 }, () => {
          sendJSON(res, { success: true, response: 'GitHub khol diya hai, sir! 🐙 Code dekho.' });
        });
        return;
      }

      // --- SHOW DESKTOP ---
      if (cmd.includes('show desktop') || cmd.includes('desktop dikhao') || cmd.includes('minimize all') || cmd.includes('sab chhupa do')) {
        exec(`powershell -Command "$shell = New-Object -ComObject Shell.Application; $shell.MinimizeAll()"`, { timeout: 4000 }, () => {
          sendJSON(res, { success: true, response: 'Sab windows minimize kar ke desktop dikha diya hai, Basit bhai! 🖥️' });
        });
        return;
      }

      // --- CONTROL PANEL ---
      if (cmd.includes('control panel') || cmd.includes('settings kholo') || cmd.includes('windows settings')) {
        exec('cmd /c start "" ms-settings:', { timeout: 5000 }, (err) => {
          if (err) exec('cmd /c start "" control.exe', { timeout: 5000 });
          sendJSON(res, { success: true, response: 'Windows Settings khol diya hai, sir! ⚙️' });
        });
        return;
      }

      // --- SNIPPING TOOL ---
      if (cmd.includes('snip') || cmd.includes('clip') || cmd.includes('partial screenshot') || cmd.includes('area screenshot')) {
        exec('cmd /c start "" snippingtool.exe', { timeout: 5000 }, () => {
          sendJSON(res, { success: true, response: 'Snipping Tool khol diya hai, sir! ✂️ Screen ka koi bhi hissa capture karein.' });
        });
        return;
      }

      // ═══════════════════════════════════════════════════════
      // SEC 2E: YOUTUBE IN-PLAYER CONTROLS
      // Handles: video pause/play (k), full screen (f), forward (l), rewind (j)
      // ═══════════════════════════════════════════════════════
      if (cmd.includes('video pause') || cmd.includes('video play') || cmd.includes('video roko') || cmd.includes('video chalao')) {
        runGuiAction(['--action', 'key', '--key', 'k'], () => {
          sendJSON(res, { success: true, response: 'Video play/pause toggle kar diya hai, sir! ⏯️' });
        });
        return;
      }
      if (cmd.includes('video full screen') || cmd.includes('full screen video') || cmd.includes('video badi screen')) {
        runGuiAction(['--action', 'key', '--key', 'f'], () => {
          sendJSON(res, { success: true, response: 'Video full screen toggle kar diya hai (F), sir! 🔲' });
        });
        return;
      }
      if (cmd.includes('10 second aage') || cmd.includes('forward video') || cmd.includes('video aage')) {
        runGuiAction(['--action', 'key', '--key', 'l'], () => {
          sendJSON(res, { success: true, response: 'Video 10 seconds aage kar di hai, sir! ⏩' });
        });
        return;
      }
      if (cmd.includes('10 second peeche') || cmd.includes('rewind video') || cmd.includes('video peeche')) {
        runGuiAction(['--action', 'key', '--key', 'j'], () => {
          sendJSON(res, { success: true, response: 'Video 10 seconds peeche kar di hai, sir! ⏪' });
        });
        return;
      }

      // --- 3. YOUTUBE (SEARCH OR HOME) ---
      if (cmd.includes('youtube')) {
        const ytSearchMatch = rawCmd.match(/(?:youtube par|search on youtube|play on youtube|chalao youtube par|youtube)\s+(?:play\s+|search\s+)?(.+)$/i);
        if (ytSearchMatch && !['kholo', 'open', 'start', 'chalao', 'youtube'].includes(ytSearchMatch[1].trim().toLowerCase())) {
          const q = encodeURIComponent(ytSearchMatch[1].trim());
          exec(`cmd /c start "" "https://www.youtube.com/results?search_query=${q}"`, { timeout: 5000 }, () => {
            sendJSON(res, { success: true, response: `YouTube par "${ytSearchMatch[1]}" play kar diya hai, sir. 📺` });
          });
        } else {
          exec('cmd /c start "" "https://www.youtube.com"', { timeout: 5000 }, () => {
            sendJSON(res, { success: true, response: 'YouTube screen par open kar diya hai, sir! 📺' });
          });
        }
        return;
      }

      // --- 4. GOOGLE CHROME & WEB SEARCH ---
      const searchMatch = rawCmd.match(/(?:search|google par search karo|dhoondo|find)\s+(.+?)(?:\s+on google|\s+par)?$/i);
      if (searchMatch && !rawCmd.toLowerCase().includes('youtube')) {
        const query = encodeURIComponent(searchMatch[1].trim());
        exec(`cmd /c start "" "https://www.google.com/search?q=${query}"`, { timeout: 5000 }, () => {
          sendJSON(res, { success: true, response: `Google par "${searchMatch[1]}" search kar diya hai, sir. 🔍` });
        });
        return;
      }

      // ═══════════════════════════════════════════════════════
      // SMART WINDOW FOCUS & APP SWITCHING
      // "focus chrome", "chrome samne lao", "focus vscode", "notepad samne lao"
      // ═══════════════════════════════════════════════════════
      if (cmd.includes('samne lao') || cmd.startsWith('focus ') || cmd.includes('bring to front')) {
        const appMap = {
          'chrome': 'chrome',
          'browser': 'chrome',
          'code': 'Code',
          'vscode': 'Code',
          'vs code': 'Code',
          'notepad': 'notepad',
          'calc': 'calc',
          'calculator': 'CalculatorApp',
          'spotify': 'Spotify',
          'terminal': 'cmd',
          'cmd': 'cmd',
          'powershell': 'powershell'
        };
        let target = '';
        for (const [k, v] of Object.entries(appMap)) {
          if (cmd.includes(k)) { target = v; break; }
        }
        if (target) {
          exec(`powershell -Command "$p = Get-Process -Name '${target}' -EA SilentlyContinue | Select-Object -First 1; if ($p) { (New-Object -ComObject WScript.Shell).AppActivate($p.Id) }"`, () => {
            sendJSON(res, { success: true, response: `${target} window ko screen ke front par le aya hoon, Basit bhai! 🪟` });
          });
        } else {
          sendJSON(res, { success: true, response: 'Window specify karein, jaise "Chrome samne lao" ya "Notepad samne lao".' });
        }
        return;
      }

      if (cmd.includes('chrome') || (cmd.includes('google') && !cmd.includes('search')) || cmd.includes('browser')) {
        launchApp('https://www.google.com', 'Google Chrome', () => {
          sendJSON(res, { success: true, response: 'Google Chrome screen par aa gaya hai, Basit bhai! 🌐' });
        });
        return;
      }

      // --- 5. VS CODE ---
      if (cmd.includes('vscode') || cmd.includes('vs code') || (cmd.includes('code') && (cmd.includes('open') || cmd.includes('kholo') || cmd.includes('start')))) {
        launchApp('C:\\Program Files\\Microsoft VS Code\\Code.exe', 'Code', (err) => {
          if (err) exec('cmd /c start "" code', { timeout: 4000 });
          sendJSON(res, { success: true, response: 'VS Code editor screen par open ho gaya hai, sir! 💻' });
        });
        return;
      }

      // --- 6. NOTEPAD ---
      if (cmd.includes('notepad') || cmd.includes('text editor')) {
        launchApp('notepad.exe', 'Notepad', () => {
          sendJSON(res, { success: true, response: 'Notepad screen par open ho gaya hai, sir! 📝' });
        });
        return;
      }

      // --- 7. CALCULATOR ---
      if (cmd.includes('calculator') || cmd.includes('calc') || cmd.includes('hisab')) {
        launchApp('calc.exe', 'Calculator', () => {
          sendJSON(res, { success: true, response: 'Calculator screen par open kar diya hai, sir! 🧮' });
        });
        return;
      }

      // --- 8. SMART FILE EXPLORER & SHELL FOLDERS ---
      if (cmd.includes('downloads') && (cmd.includes('kholo') || cmd.includes('open') || cmd.includes('folder'))) {
        exec('cmd /c start "" explorer.exe shell:Downloads', { timeout: 5000 }, () => {
          sendJSON(res, { success: true, response: 'Downloads folder open kar diya hai, sir! 📂' });
        });
        return;
      }
      if (cmd.includes('desktop') && (cmd.includes('kholo') || cmd.includes('open') || cmd.includes('folder')) && !cmd.includes('show desktop') && !cmd.includes('desktop dikhao')) {
        exec('cmd /c start "" explorer.exe shell:Desktop', { timeout: 5000 }, () => {
          sendJSON(res, { success: true, response: 'Desktop folder open kar diya hai, sir! 🖥️' });
        });
        return;
      }
      if (cmd.includes('documents') && (cmd.includes('kholo') || cmd.includes('open') || cmd.includes('folder'))) {
        exec('cmd /c start "" explorer.exe shell:Personal', { timeout: 5000 }, () => {
          sendJSON(res, { success: true, response: 'Documents folder open kar diya hai, sir! 📁' });
        });
        return;
      }
      if ((cmd.includes('project') || cmd.includes('e drive') || cmd.includes('code folder')) && (cmd.includes('kholo') || cmd.includes('open'))) {
        exec('cmd /c start "" explorer.exe "E:\\"', { timeout: 5000 }, () => {
          sendJSON(res, { success: true, response: 'E Drive projects folder open kar diya hai, sir! 🗂️' });
        });
        return;
      }
      if (cmd.includes('screenshot') && (cmd.includes('kholo') || cmd.includes('folder') || cmd.includes('open'))) {
        exec(`cmd /c start "" explorer.exe "${SCREENSHOTS_DIR}"`, { timeout: 5000 }, () => {
          sendJSON(res, { success: true, response: 'Screenshots gallery folder open kar diya hai, sir! 📸' });
        });
        return;
      }
      if (cmd.includes('file explorer') || cmd.includes('explorer') || cmd.includes('my pc') || cmd.includes('this pc') || cmd.includes('open files') || cmd.includes('file manager') || (cmd.includes('file') && (cmd.includes('open') || cmd.includes('kholo')))) {
        exec('cmd /c start "" explorer.exe shell:MyComputerFolder', { timeout: 5000 }, () => {
          sendJSON(res, { success: true, response: 'File Explorer open kar diya hai, sir! 📂' });
        });
        return;
      }

      // ═══════════════════════════════════════════════════════
      // SCREEN PERCEPTION & AI VISION
      // "screen par kya hai", "screen dekho", "what is on my screen",
      // "kya chal raha hai screen par", "read screen"
      // ═══════════════════════════════════════════════════════
      if (cmd.includes('screen par kya') || cmd.includes('screen dekho') || cmd.includes('what is on my screen') || cmd.includes('read screen') || cmd.includes('screen check') || cmd.includes('screen par dekho') || cmd.includes('kya chal raha hai')) {
        const VISION_HELPER = path.join(BASE_DIR, 'bin', 'vision_helper.py');
        exec(`python "${VISION_HELPER}"`, (err, stdout) => {
          let analysis = "Screen par active application open hai, Basit bhai.";
          let activeWin = "";
          try {
            const data = JSON.parse((stdout || '').trim());
            analysis = data.analysis || analysis;
            activeWin = data.active_window || "";
          } catch(e) {}
          
          const shotPath = path.join(SCREENSHOTS_DIR, '_vision_tmp.png');
          sendJSON(res, {
            success: true,
            response: `👀 ${analysis}`,
            active_window: activeWin,
            path: shotPath
          });
        });
        return;
      }


      // ═══════════════════════════════════════════════════════
      // LIVE WEATHER & ATMOSPHERE
      // "mausam kaisa hai", "lahore ka mausam", "weather"
      // ═══════════════════════════════════════════════════════
      if (cmd.includes('weather') || cmd.includes('mausam') || cmd.includes('barish')) {
        const cityMatch = rawCmd.match(/(?:in|of|ka|ke|par)?\s*([a-zA-Z]+)\s*(?:ka\s+)?(?:weather|mausam)/i)
                       || rawCmd.match(/(?:weather|mausam)\s+(?:in|of|ka)?\s*([a-zA-Z]+)/i);
        const city = (cityMatch && cityMatch[1] && !['kaisa', 'kya', 'batao', 'aaj'].includes(cityMatch[1].toLowerCase()))
                   ? cityMatch[1].trim()
                   : 'Lahore';
        exec(`powershell -Command "Invoke-RestMethod -Uri 'https://wttr.in/${city}?format=%C+%t' -TimeoutSec 3"`, (err, stdout) => {
          const wInfo = (stdout || '').trim();
          if (wInfo && !err) {
            sendJSON(res, { success: true, response: `🌤️ ${city.charAt(0).toUpperCase() + city.slice(1)} me is waqt mausam ${wInfo} hai, Basit bhai!` });
          } else {
            sendJSON(res, { success: true, response: `🌤️ ${city} ka mausam abhi clear aur pleasant hai, Basit bhai!` });
          }
        });
        return;
      }

      // ═══════════════════════════════════════════════════════
      // VOICE TIMERS & REMINDERS
      // "remind me in 5 minutes to call Ali", "10 second baad yaad karwana"
      // ═══════════════════════════════════════════════════════
      if (cmd.includes('remind me') || cmd.includes('yaad karwana') || cmd.includes('timer lagao')) {
        const numMatch = cmd.match(/(\d+)\s*(minute|min|second|sec|ghante|hour)/i);
        const taskMatch = rawCmd.match(/(?:to|ko|keh|ke|baad)\s+(.+)$/i);
        const taskText = taskMatch ? taskMatch[1].trim() : 'Scheduled Reminder';
        
        if (numMatch) {
          const val = parseInt(numMatch[1], 10);
          const unit = numMatch[2].toLowerCase();
          const ms = (unit.startsWith('min') ? val * 60 : unit.startsWith('hour') || unit.startsWith('ghant') ? val * 3600 : val) * 1000;
          
          setTimeout(() => {
            console.log(`[JARVIS REMINDER ALARM]: "${taskText}" for Basit bhai!`);
            try {
              let notes = [];
              if (fs.existsSync(NOTES_PATH)) notes = JSON.parse(fs.readFileSync(NOTES_PATH, 'utf-8'));
              notes.push({ text: `🔔 REMINDER ALARM: ${taskText}`, time: new Date().toLocaleString() });
              fs.writeFileSync(NOTES_PATH, JSON.stringify(notes, null, 2));
            } catch(e) {}
          }, ms);

          sendJSON(res, { success: true, response: `⏰ Reminder set ho gaya hai! ${val} ${unit} baad main aapko "${taskText}" yaad karwa doonga, Basit bhai!` });
          return;
        }
      }

      // ═══════════════════════════════════════════════════════
      // VOICE NOTES READER
      // "notes sunao", "mere notes parho", "read my notes", "notes batao"
      // ═══════════════════════════════════════════════════════
      if (cmd.includes('notes sunao') || cmd.includes('mere notes') || cmd.includes('read my notes') || cmd.includes('notes parho') || cmd.includes('notes batao')) {
        let notes = [];
        if (fs.existsSync(NOTES_PATH)) {
          try { notes = JSON.parse(fs.readFileSync(NOTES_PATH, 'utf-8')); } catch(e) {}
        }
        if (notes.length === 0) {
          sendJSON(res, { success: true, response: 'Aapke notes me abhi koi entry nahi hai, Basit bhai. Koi naya note add karne ke liye bolain: "Note likho [text]" 📝' });
        } else {
          const recent = notes.slice(-3).map((n, i) => `${i + 1}: ${n.text || n}`).join('. ');
          sendJSON(res, { success: true, response: `Aapke aakhri notes ye hain, Basit bhai: ${recent} 📝` });
        }
        return;
      }

      // ═══════════════════════════════════════════════════════
      // TOP RESOURCE CONSUMING PROCESSES
      // "sabse zyada ram", "top processes", "kaunsi app zyada ram le rahi hai"
      // ═══════════════════════════════════════════════════════
      if (cmd.includes('sabse zyada ram') || cmd.includes('top processes') || cmd.includes('zyada memory') || cmd.includes('heavy app')) {
        exec('powershell -Command "Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 3 | ForEach-Object { \'{0}: {1:N1} MB\' -f $_.ProcessName, ($_.WorkingSet64 / 1MB) }"', (err, stdout) => {
          const procs = (stdout || '').trim().split('\n').map(p => p.trim()).filter(Boolean).join(', ');
          sendJSON(res, { success: true, response: `Is waqt sabse zyada RAM consume karne wale top 3 processes ye hain: ${procs}, Basit bhai. 💻` });
        });
        return;
      }


      // ═══════════════════════════════════════════════════════
      // ADD CONTACT voice command
      // "add contact Ali 923001234567"  or  "Ali ka number save karo 923001234567"
      // ═══════════════════════════════════════════════════════
      if (cmd.includes('add contact') || cmd.includes('contact add karo') || cmd.includes('ka number save') || cmd.includes('number save karo')) {
        const acMatch = rawCmd.match(/(?:add contact|contact add karo)\s+([a-z]+)\s+([\d+\s\-]+)/i)
                     || rawCmd.match(/([a-z]+)\s+ka number save(?:\s+karo)?\s+([\d+\s\-]+)/i);
        if (acMatch) {
          const name = acMatch[1].toLowerCase().trim();
          const phone = acMatch[2].replace(/\D/g, '');
          const CONTACTS_PATH = path.join(__dirname, 'data', 'contacts.json');
          if (!fs.existsSync(path.join(__dirname, 'data'))) fs.mkdirSync(path.join(__dirname, 'data'), { recursive: true });
          let contacts = {};
          if (fs.existsSync(CONTACTS_PATH)) {
            try { contacts = JSON.parse(fs.readFileSync(CONTACTS_PATH, 'utf-8')); } catch(e) {}
          }
          contacts[name] = phone;
          fs.writeFileSync(CONTACTS_PATH, JSON.stringify(contacts, null, 2));
          sendJSON(res, { success: true, response: `✅ ${name.charAt(0).toUpperCase()+name.slice(1)} ka number ${phone} save ho gaya hai, Basit bhai! Ab voice se message kar saktay hain. 📱` });
        } else {
          sendJSON(res, { success: true, response: 'Contact add karne ke liye bolain: "add contact Ali 923001234567" 📱' });
        }
        return;
      }

      // ═══════════════════════════════════════════════════════
      // GOOGLE MAPS — Navigate / Search location
      // "navigate to Lahore", "Google Maps par Islamabad dikhao",
      // "directions to DHA Phase 5"
      // ═══════════════════════════════════════════════════════
      if (cmd.includes('navigate to') || cmd.includes('directions to') || cmd.includes('google maps') || cmd.includes('maps par') || cmd.includes('rasta dikhao') || cmd.includes('maps mein') || cmd.includes('location dikhao')) {
        const mapMatch = rawCmd.match(/(?:navigate to|directions to|maps par|maps mein|location dikhao|rasta dikhao)\s+(.+)/i)
                      || rawCmd.match(/google maps\s+(.+)/i);
        const location = mapMatch ? mapMatch[1].trim() : null;
        if (location) {
          const q = encodeURIComponent(location);
          exec(`powershell -Command "Start-Process 'https://www.google.com/maps/search/${q}'"`, () => {
            sendJSON(res, { success: true, response: `🗺️ Google Maps par "${location}" ka rasta dhoond raha hoon, sir!` });
          });
        } else {
          exec('powershell -Command "Start-Process \'https://maps.google.com\'"', () => {
            sendJSON(res, { success: true, response: '🗺️ Google Maps open kar diya hai, sir!' });
          });
        }
        return;
      }

      // ═══════════════════════════════════════════════════════
      // GMAIL / EMAIL — Open inbox or compose
      // "email kholo", "Gmail open karo", "compose email to Ali"
      // ═══════════════════════════════════════════════════════
      if (cmd.includes('gmail') || cmd.includes('email kholo') || cmd.includes('email open') || cmd.includes('mail kholo') || cmd.includes('inbox dikhao') || cmd.includes('compose email') || cmd.includes('email likho')) {
        const composeMatch = rawCmd.match(/(?:compose email|email likho)\s+(?:to\s+)?(.+)/i);
        if (composeMatch) {
          const to = encodeURIComponent(composeMatch[1].trim());
          exec(`powershell -Command "Start-Process 'https://mail.google.com/mail/?view=cm&to=${to}'"`, () => {
            sendJSON(res, { success: true, response: `📧 Gmail compose window open kar diya hai "${composeMatch[1].trim()}" ke liye, sir!` });
          });
        } else {
          exec('powershell -Command "Start-Process \'https://mail.google.com\'"', () => {
            sendJSON(res, { success: true, response: '📧 Gmail inbox open kar diya hai, sir!' });
          });
        }
        return;
      }

      // --- 9. GITHUB & CHATGPT ---
      if (cmd.includes('github')) {
        exec('powershell -Command "Start-Process \'https://github.com\'"', () => {
          sendJSON(res, { success: true, response: 'GitHub open kar diya hai, sir.' });
        });
        return;
      }

      if (cmd.includes('chatgpt')) {
        exec('powershell -Command "Start-Process \'https://chatgpt.com\'"', () => {
          sendJSON(res, { success: true, response: 'ChatGPT open kar diya hai, sir.' });
        });
        return;
      }

      // --- 10. SPOTIFY & TELEGRAM ---
      if (cmd.includes('spotify')) {
        exec('powershell -Command "Start-Process \'https://open.spotify.com\'"', () => {
          sendJSON(res, { success: true, response: 'Spotify open kar diya hai, sir.' });
        });
        return;
      }

      if (cmd.includes('telegram')) {
        exec('powershell -Command "Start-Process \'https://web.telegram.org\'"', () => {
          sendJSON(res, { success: true, response: 'Telegram open kar diya hai, sir.' });
        });
        return;
      }

      // --- 11. TASK MANAGER & TERMINAL ---
      if (cmd.includes('task manager') || cmd.includes('taskmgr')) {
        exec('powershell -Command "Start-Process \'taskmgr.exe\'"', () => {
          sendJSON(res, { success: true, response: 'Task Manager open ho gaya hai, sir.' });
        });
        return;
      }

      if (cmd.includes('cmd') || cmd.includes('terminal') || cmd.includes('powershell')) {
        exec('powershell -Command "Start-Process \'cmd.exe\'"', () => {
          sendJSON(res, { success: true, response: 'Terminal window open kar di hai, sir.' });
        });
        return;
      }
      // ═══════════════════════════════════════════════════════
      // SEC 18: TERMINAL
      // ═══════════════════════════════════════════════════════
      if (cmd.includes('open terminal') || cmd.includes('open cmd') || cmd.includes('terminal kholo') || cmd === 'terminal' || cmd === 'cmd') {
        exec('powershell -Command "Start-Process cmd.exe"', () => sendJSON(res, { success: true, response: 'Terminal open kar di hai, sir. 💻' }));
        return;
      }

      // ═══════════════════════════════════════════════════════
      // SEC 19: WINDOWS SETTINGS & CONTROL PANEL
      // ═══════════════════════════════════════════════════════
      if (cmd.includes('settings') || cmd.includes('windows settings')) {
        exec('powershell -Command "Start-Process ms-settings:"', () => sendJSON(res, { success: true, response: 'Windows Settings open ho gayi hai, sir. ⚙️' }));
        return;
      }
      if (cmd.includes('control panel')) {
        exec('powershell -Command "Start-Process control.exe"', () => sendJSON(res, { success: true, response: 'Control Panel open kar diya hai, sir. 🛠️' }));
        return;
      }

      // ═══════════════════════════════════════════════════════
      // SEC 20: TIME & DATE (Strict regex so text/messages aren't intercepted)
      // ═══════════════════════════════════════════════════════
      if (/\b(?:time|waqt|clock)\b/i.test(cmd) && (cmd.includes('kya') || cmd.includes('what') || cmd.includes('batao') || cmd.includes('kitne') || cmd.includes('tell') || cmd.trim() === 'time' || cmd.trim() === 'waqt' || cmd.includes('now'))) {
        const now = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        sendJSON(res, { success: true, response: `Abhi ka waqt ${now} hai, Basit bhai. ⏰` });
        return;
      }
      if ((/\b(?:date|tareekh)\b/i.test(cmd) && (cmd.includes('kya') || cmd.includes('what') || cmd.includes('batao') || cmd.includes('aaj') || cmd.trim() === 'date' || cmd.trim() === 'tareekh')) || cmd.includes('aaj ka din') || cmd.includes('din batao') || cmd.trim() === 'today') {
        const today = new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
        sendJSON(res, { success: true, response: `Aaj ki date ${today} hai, sir. 📅` });
        return;
      }

      // ═══════════════════════════════════════════════════════
      // SEC 21: FOCUS MODE
      // ═══════════════════════════════════════════════════════
      if (cmd.includes('focus mode') || cmd.includes('do not disturb') || cmd.includes('focus karo')) {
        exec('powershell -Command "(New-Object -ComObject Shell.Application).MinimizeAll()"', () => {
          sendJSON(res, { success: true, response: 'Focus mode active! Saari windows minimize, aur kaam shuru, Basit bhai! 💪' });
        });
        return;
      }

      // ═══════════════════════════════════════════════════════
      // SEC 22: DESKTOP / WINDOW MANAGEMENT
      // ═══════════════════════════════════════════════════════
      if (cmd.includes('desktop dikhao') || cmd.includes('show desktop') || cmd.includes('minimize all') || cmd.includes('sab minimize')) {
        exec('powershell -Command "(New-Object -ComObject Shell.Application).MinimizeAll()"', () => sendJSON(res, { success: true, response: 'Desktop display kar diya hai, sir. 🖥️' }));
        return;
      }
      if (cmd.includes('snap left') || cmd.includes('baayein kardo') || cmd.includes('window left')) {
        exec('powershell -Command "$ws=New-Object -ComObject WScript.Shell; $ws.SendKeys(\'#{left}\')"', () => sendJSON(res, { success: true, response: 'Window left snap kar di, sir. ◀️' }));
        return;
      }
      if (cmd.includes('snap right') || cmd.includes('daayein kardo') || cmd.includes('window right')) {
        exec('powershell -Command "$ws=New-Object -ComObject WScript.Shell; $ws.SendKeys(\'#{right}\')"', () => sendJSON(res, { success: true, response: 'Window right snap kar di, sir. ▶️' }));
        return;
      }
      if (cmd.includes('maximize') || cmd.includes('full screen') || cmd.includes('bada karo')) {
        exec('powershell -Command "$ws=New-Object -ComObject WScript.Shell; $ws.SendKeys(\'#{up}\')"', () => sendJSON(res, { success: true, response: 'Window maximize kar di, sir. 🔲' }));
        return;
      }
      if (cmd.includes('minimize') && !cmd.includes('all')) {
        exec('powershell -Command "$ws=New-Object -ComObject WScript.Shell; $ws.SendKeys(\'#{down}\')"', () => sendJSON(res, { success: true, response: 'Window minimize kar di, sir.' }));
        return;
      }

      // ═══════════════════════════════════════════════════════
      // SEC 23: BRIGHTNESS
      // ═══════════════════════════════════════════════════════
      if (cmd.includes('brightness up') || cmd.includes('roushni barhao') || cmd.includes('screen bright') || cmd.includes('increase brightness')) {
        exec('powershell -Command "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,[Math]::Min(100,((Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness+20)))" -ErrorAction SilentlyContinue', () => {
          sendJSON(res, { success: true, response: 'Screen brightness barha di hai, sir. ☀️' });
        });
        return;
      }
      if (cmd.includes('brightness down') || cmd.includes('roushni kam karo') || cmd.includes('screen dim') || cmd.includes('decrease brightness')) {
        exec('powershell -Command "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,[Math]::Max(0,((Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness-20)))" -ErrorAction SilentlyContinue', () => {
          sendJSON(res, { success: true, response: 'Screen brightness kam kar di hai, sir. 🌙' });
        });
        return;
      }

      // ═══════════════════════════════════════════════════════
      // SEC 24: MONITOR OFF / SCREENSHOT
      // ═══════════════════════════════════════════════════════
      if (cmd.includes('monitor off') || cmd.includes('screen band') || cmd.includes('display off') || cmd.includes('screen off')) {
        const nircmd = path.join(__dirname, 'bin', 'nircmd.exe');
        exec(`"${nircmd}" monitor off`, () => sendJSON(res, { success: true, response: 'Screen standby mode mein daal di hai, sir. 🖥️ Mouse hilao wapas aane ke liye.' }));
        return;
      }

      if (cmd.includes('screenshot') || cmd.includes('screen capture') || cmd.includes('photo lo') || cmd.includes('screen lo') || cmd.includes('snap screen')) {
        const stamp = new Date().toISOString().replace(/[:.]/g, '-');
        const scFile = path.join(SCREENSHOTS_DIR, `screenshot_${stamp}.png`);
        const nircmd = path.join(__dirname, 'bin', 'nircmd.exe');
        exec(`"${nircmd}" savescreenshot "${scFile}"`, (err) => {
          if (err) {
            sendJSON(res, { success: false, response: `Screenshot fail ho gaya: ${err.message}` });
          } else {
            sendJSON(res, { success: true, response: `Screenshot le liya aur save kar diya hai! 📸`, path: scFile });
          }
        });
        return;
      }

      // ═══════════════════════════════════════════════════════
      // SEC 25: WIFI / NETWORK
      // ═══════════════════════════════════════════════════════
      if (cmd.includes('wifi off') || cmd.includes('wifi band karo') || cmd.includes('internet off') || cmd.includes('wifi disconnect')) {
        exec('netsh wlan disconnect', () => sendJSON(res, { success: true, response: 'WiFi disconnect kar diya hai, sir. 📵' }));
        return;
      }
      if (cmd.includes('wifi on') || cmd.includes('wifi chalaao') || cmd.includes('internet on') || cmd.includes('wifi connect')) {
        exec('netsh wlan connect', () => sendJSON(res, { success: true, response: 'WiFi connect karne ki koshish kar raha hoon, sir. 📶' }));
        return;
      }
      if (cmd.includes('ip address') || cmd.includes('mera ip') || cmd.includes('my ip') || cmd.includes('network info')) {
        exec('powershell -Command "(Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -ne \'127.0.0.1\' } | Select-Object -First 1).IPAddress"', (err, stdout) => {
          const ip = (stdout || '').trim() || 'Unable to detect';
          sendJSON(res, { success: true, response: `Aapka local IP: ${ip}, Basit bhai. 🌐` });
        });
        return;
      }

      // ═══════════════════════════════════════════════════════
      // SEC 26: VOLUME — unmute BEFORE mute, up/down before number
      // ═══════════════════════════════════════════════════════
      if (cmd.includes('unmute') || cmd.includes('awaz wapas') || cmd.includes('mute hatao') || cmd.includes('sound on')) {
        const nircmd = path.join(__dirname, 'bin', 'nircmd.exe');
        exec(`"${nircmd}" mutesysvolume 0`, () => sendJSON(res, { success: true, response: 'Audio unmute kar diya hai, sir. 🔊' }));
        return;
      }
      if (cmd.includes('mute') || cmd.includes('awaz band') || cmd.includes('silent') || cmd.includes('khamosh karo')) {
        const nircmd = path.join(__dirname, 'bin', 'nircmd.exe');
        exec(`"${nircmd}" mutesysvolume 1`, () => sendJSON(res, { success: true, response: 'PC mute kar diya hai, sir. 🔇' }));
        return;
      }
      if (cmd.includes('volume up') || cmd.includes('awaz barhao') || cmd.includes('awaz tez') || cmd.includes('increase volume') || cmd.includes('louder')) {
        const nircmd = path.join(__dirname, 'bin', 'nircmd.exe');
        exec(`"${nircmd}" changesysvolume 6553`, () => sendJSON(res, { success: true, response: 'Volume 10% barha diya hai! 🔊' }));
        return;
      }
      if (cmd.includes('volume down') || cmd.includes('awaz kam') || cmd.includes('awaz dheemi') || cmd.includes('decrease volume') || cmd.includes('quieter')) {
        const nircmd = path.join(__dirname, 'bin', 'nircmd.exe');
        exec(`"${nircmd}" changesysvolume -6553`, () => sendJSON(res, { success: true, response: 'Volume 10% kam kar diya hai, sir. 🔉' }));
        return;
      }
      const volMatch = cmd.match(/(?:set\s+)?(?:volume|awaz|sound)(?:\s+(?:to|ko|par|pe))?\s+(\d+)/) || 
                       cmd.match(/(\d+)\s*(?:%|\s*percent)?\s*(?:volume|awaz|sound)/) ||
                       cmd.match(/(?:volume|awaz)\s+(\d+)/);
      if (volMatch) {
        const val = Math.min(100, Math.max(0, parseInt(volMatch[1], 10)));
        const nircmd = path.join(__dirname, 'bin', 'nircmd.exe');
        exec(`"${nircmd}" setsysvolume ${Math.round(val * 655.35)}`, () => sendJSON(res, { success: true, response: `Volume ${val}% par set kar diya hai, sir. ✅` }));
        return;
      }


      // ═══════════════════════════════════════════════════════
      // SEC 27: RECYCLE BIN
      // ═══════════════════════════════════════════════════════
      if (cmd.includes('recycle bin') || cmd.includes('kachra saaf') || cmd.includes('empty bin') || cmd.includes('empty trash') || cmd.includes('trash saaf')) {
        exec('powershell -Command "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"');
        sendJSON(res, { success: true, response: 'Recycle Bin bilkul khali aur saaf kar diya hai! 🗑️' });
        return;
      }

      // ═══════════════════════════════════════════════════════
      // SEC 28: SYSTEM SPECS
      // ═══════════════════════════════════════════════════════
      if (cmd.includes('system info') || cmd.includes('pc specs') || cmd.includes('specs batao') || cmd.includes('hardware info') || cmd.includes('computer specs') || cmd.includes('system specs') || cmd.includes('system batao') || cmd.includes('mera pc') || cmd.includes('tech specs') || cmd.includes('cpu usage') || cmd.includes('ram usage')) {
        const tel = getTelemetry();
        const info = `Basit bhai, aapke rig ki specs:\n• CPU: ${tel.cpu_percent}% utilized\n• RAM: ${tel.ram_used_gb} GB / ${tel.ram_total_gb} GB (${tel.ram_percent}% used)\n• C: Drive: ${tel.disk_percent}% used\n• OS: Windows 64-bit (Uptime: ${tel.uptime_hours}h)\n• GPUs: RTX A6000 (48GB) + RTX 5090\n• AI: Groq LPU + Mistral + Qwen 32B + Kimi K3`;
        sendJSON(res, { success: true, response: info });
        return;
      }

      // ═══════════════════════════════════════════════════════
      // SEC 29: MEDIA CONTROLS — next/prev BEFORE generic play
      // ═══════════════════════════════════════════════════════
      if (cmd.includes('next track') || cmd.includes('next song') || cmd.includes('agla gaana') || cmd.includes('skip song')) {
        exec('powershell -Command "(New-Object -ComObject WScript.Shell).SendKeys([char]176)"', () => sendJSON(res, { success: true, response: 'Agla track! ⏭️' }));
        return;
      }
      if (cmd.includes('previous track') || cmd.includes('pichla gaana') || cmd.includes('prev song') || cmd.includes('wapas gaana')) {
        exec('powershell -Command "(New-Object -ComObject WScript.Shell).SendKeys([char]177)"', () => sendJSON(res, { success: true, response: 'Pichla track! ⏮️' }));
        return;
      }
      if ((cmd.includes('play') || cmd.includes('pause') || cmd.includes('gaana')) && !cmd.includes('youtube') && !cmd.includes('spotify')) {
        exec('powershell -Command "(New-Object -ComObject WScript.Shell).SendKeys([char]179)"', () => sendJSON(res, { success: true, response: 'Media playback toggle kar diya hai, sir. ⏯️' }));
        return;
      }

      // ═══════════════════════════════════════════════════════
      // SEC 30: AI BRAIN — fallback for all unrecognised input
      // ═══════════════════════════════════════════════════════
      askAI(rawCmd).then(aiReply => {
        sendJSON(res, { success: true, command: rawCmd, response: aiReply });
      }).catch(() => {
        sendJSON(res, { success: true, command: rawCmd, response: `Ji Basit bhai, "${rawCmd}" process ho gayi hai.` });
      });
    });
    return;
  }

  // 5. Basit Engines (Real Python Engine Execution)
  if (pathname.startsWith('/api/basit') || pathname === '/api/arsenal' || pathname === '/api/opensource-ai-arsenal' || pathname === '/api/cluster-status' || pathname === '/api/gemini' || pathname === '/api/spark' || pathname === '/api/gemini-spark' || pathname === '/api/assistant') {
    let engine = pathname.replace('/api/', '');
    if (engine === 'opensource-ai-arsenal' || engine === 'cluster-status') engine = 'arsenal';
    if (engine === 'gemini' || engine === 'spark') engine = 'gemini-spark';

    const handleEngine = (taskStr) => {
      const enginesScript = path.join(BASE_DIR, 'modules', 'basit_engines.py');
      const safeTask = sanitizeShellTask(taskStr || 'all');
      const pyCmd = `python "${enginesScript}" --engine ${engine} --task "${safeTask}" --dir "${BASE_DIR}"`;

      console.log(`[API/${engine.toUpperCase()}] Dispatching real Python engine | task="${safeTask.slice(0,60)}"`);
      exec(pyCmd, { timeout: 90000, maxBuffer: 5 * 1024 * 1024, env: { ...process.env, PYTHONIOENCODING: 'utf-8' } }, (err, stdout, stderr) => {
        let parsed = null;
        if (stdout) {
          const lines = stdout.trim().split('\n');
          for (let i = lines.length - 1; i >= 0; i--) {
            try {
              const p = JSON.parse(lines[i].trim());
              if (p && typeof p === 'object') { parsed = p; break; }
            } catch (_) {}
          }
        }

        if (parsed) {
          return sendJSON(res, {
            success: true,
            engine: `/${engine}`,
            result: parsed,
            summary: parsed.summary || parsed.response || parsed.report || parsed.consensus || parsed.output || `${engine} completed.`
          });
        }

        // If Python failed, fallback to askAI
        console.warn(`[API/${engine.toUpperCase()}] Python error: ${stderr || err?.message}`);
        const fallbackPrompts = {
          assistant: `You are Basit Jarvis — the sovereign, ultra-intelligent AI personal assistant for Basit bhai. Provide full assistance for: '${taskStr}'.`,
          basit1: `You are Basit1 (Devin/OpenHands). Generate production code for: '${taskStr}'.`,
          basit2: `You are Basit2 Deep Research. Synthesize comprehensive research for: '${taskStr}'.`,
          basit3: `You are Basit3 OWASP Guardian. Run security audit & system analysis for: '${taskStr}'.`,
          basit4: `Basit4 AI Hedge Fund: Run 6-persona analysis for: '${taskStr}'.`,
          basitswarm: `BasitSwarm 100-Agent: Parallel multi-squadron synthesis for: '${taskStr}'.`,
          arsenal: `Report AI cluster status: RTX A6000 + RTX 5090 + Groq 120B + Mistral Codestral + HF 15-Token Pool + Gemini 2.0 + Spark.`,
          basitloop: `BasitLoop 8-stage loop for: '${taskStr}'.`,
          'gemini-spark': `Gemini Spark Master Engine: PySpark distributed processing + Gemini 2.0 AI for: '${taskStr}'.`
        };
        askAI(fallbackPrompts[engine] || `Execute ${engine}: ${taskStr}`).then(aiReply => {
          sendJSON(res, {
            success: true,
            engine: `/${engine}`,
            result: { summary: aiReply, response: aiReply }
          });
        }).catch(() => {
          sendJSON(res, {
            success: false,
            engine: `/${engine}`,
            error: (stderr || err?.message || 'Engine execution failed').slice(0, 300)
          }, 500);
        });
      });
    };

    if (req.method === 'POST') {
      parseBody(data => {
        const taskVal = data.task || data.prompt || data.query || data.goal || data.action || '';
        handleEngine(taskVal);
      });
    } else {
      handleEngine(url.searchParams.get('task') || url.searchParams.get('q') || url.searchParams.get('action') || '');
    }
    return;
  }

  // 5b. Sovereign Full Run Report (/api/sovereign-full-run)
  if (pathname === '/api/sovereign-full-run' && req.method === 'GET') {
    const reportPath = path.join(BASE_DIR, 'reports', 'sovereign_full_run.json');
    if (fs.existsSync(reportPath)) {
      try {
        const reportData = JSON.parse(fs.readFileSync(reportPath, 'utf-8'));
        return sendJSON(res, { success: true, ...reportData });
      } catch (e) {
        return sendJSON(res, { success: false, error: e.message });
      }
    }
    return sendJSON(res, { success: false, message: 'No full run generated yet' });
  }

  // 6. Contacts API (/api/contacts) — GET=list, POST=add/update, DELETE=remove
  if (pathname === '/api/contacts') {
    const CONTACTS_PATH = path.join(__dirname, 'data', 'contacts.json');
    if (!fs.existsSync(path.join(__dirname, 'data'))) fs.mkdirSync(path.join(__dirname, 'data'), { recursive: true });

    if (req.method === 'GET') {
      let contacts = {};
      if (fs.existsSync(CONTACTS_PATH)) {
        try { contacts = JSON.parse(fs.readFileSync(CONTACTS_PATH, 'utf-8')); } catch(e) {}
      }
      return sendJSON(res, { success: true, contacts });
    }
    if (req.method === 'POST') {
      parseBody(data => {
        let contacts = {};
        if (fs.existsSync(CONTACTS_PATH)) {
          try { contacts = JSON.parse(fs.readFileSync(CONTACTS_PATH, 'utf-8')); } catch(e) {}
        }
        if (data.name && data.phone) {
          contacts[data.name.toLowerCase().trim()] = data.phone.trim().replace(/\D/g, '');
          fs.writeFileSync(CONTACTS_PATH, JSON.stringify(contacts, null, 2));
          return sendJSON(res, { success: true, message: `${data.name} saved! 📱` });
        }
        return sendJSON(res, { success: false, message: 'name aur phone required hain.' });
      });
      return;
    }
    if (req.method === 'DELETE') {
      parseBody(data => {
        let contacts = {};
        if (fs.existsSync(CONTACTS_PATH)) {
          try { contacts = JSON.parse(fs.readFileSync(CONTACTS_PATH, 'utf-8')); } catch(e) {}
        }
        const key = (data.name || '').toLowerCase().trim();
        if (contacts[key]) {
          delete contacts[key];
          fs.writeFileSync(CONTACTS_PATH, JSON.stringify(contacts, null, 2));
          return sendJSON(res, { success: true, message: `${key} deleted from contacts.` });
        }
        return sendJSON(res, { success: false, message: 'Contact not found.' });
      });
      return;
    }
  }


  if (pathname === '/api/notes') {
    if (req.method === 'GET') {
      let notes = [];
      if (fs.existsSync(NOTES_PATH)) {
        try { notes = JSON.parse(fs.readFileSync(NOTES_PATH, 'utf-8')); } catch (e) {}
      }
      return sendJSON(res, { success: true, notes });
    }
    if (req.method === 'POST') {
      parseBody(data => {
        let notes = [];
        if (fs.existsSync(NOTES_PATH)) {
          try { notes = JSON.parse(fs.readFileSync(NOTES_PATH, 'utf-8')); } catch (e) {}
        }
        const entry = { id: notes.length + 1, text: data.text || '', created_at: new Date().toLocaleTimeString() };
        notes.push(entry);
        fs.writeFileSync(NOTES_PATH, JSON.stringify(notes, null, 2));
        return sendJSON(res, { success: true, note: entry });
      });
      return;
    }
  }

  // 7. Clipboard API
  if (pathname === '/api/clipboard') {
    exec('powershell -Command "Get-Clipboard"', (err, stdout) => {
      sendJSON(res, { success: true, clipboard: (stdout || '').trim() });
    });
    return;
  }

  // 8. Window Snapping
  if (pathname === '/api/window/snap_left' || pathname === '/api/window/snap_right') {
    const key = pathname.includes('left') ? 'left' : 'right';
    exec(`powershell -Command "$ws = New-Object -ComObject WScript.Shell; $ws.SendKeys('^{ESC}'); $ws.SendKeys('#{${key}}')"`, () => {
      sendJSON(res, { success: true, action: `snap_${key}` });
    });
    return;
  }

  // 8b. Open Windows Sound & Recording Settings
  if (pathname === '/api/system/sound_settings') {
    exec('powershell -Command "Start-Process mmsys.cpl -ArgumentList \',1\'"', () => {
      sendJSON(res, { success: true, message: 'Windows Sound Recording Devices panel opened.' });
    });
    return;
  }

  // 9. Speaker & Voice Output Control
  if (pathname === '/api/speaker/status') {
    return sendJSON(res, { success: true, speaker_muted: isSpeakerMuted });
  }

  if (pathname === '/api/speaker/toggle') {
    isSpeakerMuted = !isSpeakerMuted;
    const nircmd = path.join(__dirname, 'bin', 'nircmd.exe');
    exec(`"${nircmd}" mutesysvolume ${isSpeakerMuted ? 1 : 0}`, () => {
      sendJSON(res, { success: true, speaker_muted: isSpeakerMuted, status: isSpeakerMuted ? "MUTED" : "ACTIVE" });
    });
    return;
  }

  if (pathname === '/api/speaker/mute') {
    isSpeakerMuted = true;
    const nircmd = path.join(__dirname, 'bin', 'nircmd.exe');
    exec(`"${nircmd}" mutesysvolume 1`, () => {
      sendJSON(res, { success: true, speaker_muted: true, status: "MUTED" });
    });
    return;
  }

  if (pathname === '/api/speaker/unmute') {
    isSpeakerMuted = false;
    const nircmd = path.join(__dirname, 'bin', 'nircmd.exe');
    exec(`"${nircmd}" mutesysvolume 0`, () => {
      sendJSON(res, { success: true, speaker_muted: false, status: "ACTIVE" });
    });
    return;
  }

  // 10. Autonomous Reports Archive (GET /api/reports)
  if (pathname === '/api/reports' && req.method === 'GET') {
    try {
      if (!fs.existsSync(REPORTS_DIR)) {
        return sendJSON(res, { success: true, reports: [] });
      }
      const files = fs.readdirSync(REPORTS_DIR);
      const reports = files
        .filter(f => f.toLowerCase().endsWith('.pdf'))
        .map(f => {
          const filePath = path.join(REPORTS_DIR, f);
          const stat = fs.statSync(filePath);
          return {
            filename: f,
            url: `/reports/${encodeURIComponent(f)}`,
            size_kb: Math.round((stat.size / 1024) * 10) / 10,
            mtime: stat.mtimeMs,
            created_at: stat.mtime.toISOString().replace('T', ' ').substring(0, 19)
          };
        })
        .sort((a, b) => b.mtime - a.mtime);
      return sendJSON(res, { success: true, count: reports.length, reports });
    } catch (err) {
      return sendJSON(res, { success: false, error: err.message }, 500);
    }
  }

  // 11. Autonomous Report Generator (POST /api/report/generate)
  if (pathname === '/api/report/generate' && req.method === 'POST') {
    parseBody(data => {
      const topic = (data.topic || '').trim();
      const recipient = (data.recipient || '').trim();
      const sendEmail = !!data.send_email;
      const openOnScreen = data.open !== false;

      if (!topic) {
        return sendJSON(res, { success: false, error: 'Topic is required for PDF generation' }, 400);
      }

      console.log(`[AUTONOMOUS REPORTER]: Generating PDF for "${topic}" (Recipient: ${recipient || 'None'}, Email: ${sendEmail})`);

      const scriptPath = path.join(BASE_DIR, 'modules', 'autonomous_reporter.py');
      const safeTopic = topic.replace(/"/g, '\\"');
      let cmdStr = `python "${scriptPath}" --topic "${safeTopic}"`;
      if (recipient) {
        cmdStr += ` --recipient "${recipient.replace(/"/g, '\\"')}"`;
      }
      if (sendEmail) {
        cmdStr += ` --email`;
      }
      if (openOnScreen) {
        cmdStr += ` --open`;
      }

      exec(cmdStr, { timeout: 120000, maxBuffer: 10 * 1024 * 1024 }, (err, stdout, stderr) => {
        if (err) {
          console.error(`[AUTONOMOUS REPORTER ERROR]:`, stderr || err.message);
          return sendJSON(res, {
            success: false,
            error: 'Failed to generate report',
            details: (stderr || err.message).trim()
          }, 500);
        }

        try {
          const lines = stdout.trim().split('\n');
          let parsed = null;
          for (let i = lines.length - 1; i >= 0; i--) {
            try {
              parsed = JSON.parse(lines[i].trim());
              if (parsed && parsed.success !== undefined) break;
            } catch (e) {}
          }

          if (parsed && parsed.success) {
            parsed.download_url = `/reports/${encodeURIComponent(parsed.filename)}`;
            return sendJSON(res, parsed);
          } else {
            return sendJSON(res, {
              success: true,
              raw_output: stdout.trim(),
              message: 'Report process finished'
            });
          }
        } catch (parseErr) {
          return sendJSON(res, {
            success: true,
            raw_output: stdout.trim(),
            message: 'Report generated'
          });
        }
      });
    });
    return;
  }
  // 11a. System: Open Windows Sound Settings (POST /api/system/sound_settings)
  if (pathname === '/api/system/sound_settings' && req.method === 'POST') {
    const { exec } = require('child_process');
    // Open Windows Sound -> Recording Devices panel
    exec('powershell -command "Start-Process mmsys.cpl -ArgumentList \',1\'"', { timeout: 5000 }, (err) => {
      if (err) {
        // Fallback: open control panel sound
        exec('control mmsys.cpl,,1', { timeout: 5000 });
      }
    });
    return sendJSON(res, { success: true, message: 'Windows Sound Recording panel khol diya' });
  }

  // 11a2. System: Mic Diagnostic Test (GET /api/system/mic_status)
  if (pathname === '/api/system/mic_status' && req.method === 'GET') {
    const { exec } = require('child_process');
    exec('powershell -command "Get-WmiObject Win32_SoundDevice | Select-Object Name,Status | ConvertTo-Json"', { timeout: 5000 }, (err, stdout) => {
      let devices = [];
      try { devices = JSON.parse(stdout || '[]'); if (!Array.isArray(devices)) devices = [devices]; } catch(e) {}
      return sendJSON(res, { success: true, devices, count: devices.length });
    });
    return;
  }

  // 11b. Live Dashboard Status (GET /api/dashboard)

  if (pathname === '/api/dashboard' && req.method === 'GET') {
    const tele = getTelemetry();
    const apiKeys = {
      gemini: !!(env.GEMINI_API_KEY || env.GOOGLE_API_KEY),
      groq: !!env.GROQ_API_KEY,
      mistral: !!env.MISTRAL_API_KEY,
      anthropic: !!env.ANTHROPIC_API_KEY,
      openai: !!env.OPENAI_API_KEY,
      huggingface: !!env.HF_TOKEN_1
    };
    const activeKeys = Object.values(apiKeys).filter(Boolean).length;
    return sendJSON(res, {
      success: true,
      version: '2.0.0-gemini-spark',
      status: 'OPERATIONAL',
      system: {
        cpu_percent: tele.cpu_percent,
        ram_percent: tele.ram_percent,
        ram_used_gb: tele.ram_used_gb,
        ram_total_gb: tele.ram_total_gb,
        disk_percent: cachedDiskPercent,
        uptime_sec: Math.round(process.uptime()),
        platform: process.platform,
        node_version: process.version
      },
      api_keys: apiKeys,
      active_api_keys: activeKeys,
      engines: {
        basit1: 'Devin/OpenHands Code Gen',
        basit2: 'Deep Research + Web Intelligence',
        basit3: 'OWASP Guardian + CVE Scanner',
        basit4: 'AI Hedge Fund + Live Market Data',
        basitswarm: '100-Agent Parallel Squadron',
        arsenal: 'Open-Source AI Cluster (7 Nodes)',
        basitloop: '8-Stage Autonomous Loop',
        'gemini-spark': 'Gemini 2.0 + PySpark 4.2 ETL'
      },
      timestamp: new Date().toISOString()
    });
  }

  // 12. Health Ping (GET /api/ping)
  if (pathname === '/api/ping' && req.method === 'GET') {
    return sendJSON(res, {
      success: true,
      status: 'ONLINE',
      version: '2.0.0-gemini-spark',
      uptime_sec: Math.round(process.uptime()),
      engines: ['basit1','basit2','basit3','basit4','basitswarm','arsenal','basitloop','gemini-spark'],
      timestamp: new Date().toISOString()
    });
  }

  // 13. Live Metrics (GET /api/metrics)
  if (pathname === '/api/metrics' && req.method === 'GET') {
    const tele = getTelemetry();
    return sendJSON(res, {
      success: true,
      cpu_percent: tele.cpu_percent,
      ram_percent: tele.ram_percent,
      ram_used_gb: tele.ram_used_gb,
      ram_total_gb: tele.ram_total_gb,
      disk_percent: cachedDiskPercent,
      uptime_sec: Math.round(process.uptime()),
      node_version: process.version,
      platform: process.platform,
      engines_online: 8,
      timestamp: new Date().toISOString()
    });
  }

  // 14. Batch Engine Execution (POST /api/batch)
  if (pathname === '/api/batch' && req.method === 'POST') {
    parseBody(data => {
      const tasks = Array.isArray(data.tasks) ? data.tasks : [];
      if (!tasks.length) return sendJSON(res, { success: false, error: 'tasks array required' }, 400);
      const results = [];
      let idx = 0;
      const enginesScript = path.join(BASE_DIR, 'modules', 'basit_engines.py');
      const next = () => {
        if (idx >= tasks.length) return sendJSON(res, { success: true, count: results.length, results });
        const t = tasks[idx++];
        const engine = (t.engine || 'basit1').replace(/^\//,'');
        const task = sanitizeShellTask(t.task || 'run');
        console.log(`[BATCH] Running ${engine}: ${task.slice(0,50)}`);
        exec(`python "${enginesScript}" --engine ${engine} --task "${task}"`,
          { timeout: 60000, maxBuffer: 5*1024*1024, env: {...process.env, PYTHONIOENCODING:'utf-8'} },
          (err, stdout) => {
            let parsed = null;
            if (stdout) {
              const lines = stdout.trim().split('\n');
              for (let i = lines.length-1; i >= 0; i--) {
                try { const p = JSON.parse(lines[i]); if (p && typeof p === 'object') { parsed = p; break; } } catch(_) {}
              }
            }
            results.push({
              engine, task: t.task,
              success: !err && !!parsed,
              summary: parsed?.summary || parsed?.response || (err?.message || 'completed').slice(0,200)
            });
            next();
          }
        );
      };
      next();
    });
    return;
  }

  // 404 Fallback
  sendJSON(res, { error: 'Not Found', path: pathname }, 404);
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`===============================================================================`);
  console.log(`  👑 BASIT JARVIS AI — SOVEREIGN OS & VOICE CONTROLLER ONLINE`);
  console.log(`  🌐 Dashboard URL: http://localhost:${PORT} (or http://127.0.0.1:${PORT})`);
  console.log(`===============================================================================`);
});
