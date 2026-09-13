/**
 * ================================================================================
 * 👑 BASIT JARVIS AI — PM2 ECOSYSTEM CONFIG
 * ================================================================================
 * Enterprise-grade process management for Jarvis 24/7 operation.
 *
 * Install PM2:  npm install -g pm2
 * Start all:    pm2 start ecosystem.config.js
 * Stop all:     pm2 stop all
 * Restart all:  pm2 restart all
 * Status:       pm2 status
 * Live logs:    pm2 logs
 * Save config:  pm2 save
 * Auto-start:   pm2 startup (follow instructions)
 * ================================================================================
 */

module.exports = {
  apps: [
    // ── 1. MAIN JARVIS SERVER ───────────────────────────────────────────────
    {
      name: "jarvis-server",
      script: "server.js",
      cwd: __dirname,
      instances: 1,
      autorestart: true,
      watch: false,              // Don't restart on file change (prod mode)
      max_memory_restart: "500M",
      restart_delay: 3000,       // Wait 3s before restart
      max_restarts: 10,
      min_uptime: "10s",
      env: {
        NODE_ENV: "production",
        PORT: 8888,
      },
      error_file: "logs/pm2-server-error.log",
      out_file:   "logs/pm2-server-out.log",
      log_date_format: "YYYY-MM-DD HH:mm:ss",
    },

    // ── 2. TELEGRAM BOT ─────────────────────────────────────────────────────
    {
      name: "jarvis-telegram",
      script: "python",
      args: ["-X", "utf8", "modules/telegram_jarvis_bot.py"],
      cwd: __dirname,
      interpreter: "none",
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: "200M",
      restart_delay: 5000,
      max_restarts: 5,
      min_uptime: "15s",
      env: {
        PYTHONIOENCODING: "utf-8",
        PYTHONUNBUFFERED: "1",
      },
      error_file: "logs/pm2-telegram-error.log",
      out_file:   "logs/pm2-telegram-out.log",
      log_date_format: "YYYY-MM-DD HH:mm:ss",
    },

    // ── 3. TUNNEL WATCHDOG ──────────────────────────────────────────────────
    {
      name: "jarvis-tunnel",
      script: "node",
      args: ["-e", `
        const { execSync } = require('child_process');
        const lt = require('localtunnel');
        async function startTunnel() {
          try {
            const tunnel = await lt({ port: 8888, subdomain: 'basit-jarvis' });
            console.log('Tunnel LIVE:', tunnel.url);
            tunnel.on('close', () => { console.log('Tunnel closed — restarting...'); process.exit(1); });
            tunnel.on('error', e => { console.error('Tunnel error:', e.message); process.exit(1); });
          } catch(e) { console.error('Tunnel start failed:', e.message); process.exit(1); }
        }
        startTunnel();
      `],
      cwd: __dirname,
      interpreter: "none",
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: "100M",
      restart_delay: 10000,
      max_restarts: 20,
      error_file: "logs/pm2-tunnel-error.log",
      out_file:   "logs/pm2-tunnel-out.log",
      log_date_format: "YYYY-MM-DD HH:mm:ss",
    },

    // ── 4. DROPZONE WATCHER (standalone) ────────────────────────────────────
    {
      name: "jarvis-dropzone",
      script: "python",
      args: ["-X", "utf8", "-c", `
import sys, os
sys.path.insert(0, r'${__dirname.replace(/\\/g, '\\\\')}')
from modules.dropzone_watcher import start_dropzone_watcher
import time
print('[DROPZONE PM2] Starting watcher...')
observer = start_dropzone_watcher(block=False)
print('[DROPZONE PM2] Watching for files...')
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
    observer.join()
      `],
      cwd: __dirname,
      interpreter: "none",
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: "150M",
      restart_delay: 5000,
      max_restarts: 10,
      env: {
        PYTHONIOENCODING: "utf-8",
        PYTHONUNBUFFERED: "1",
      },
      error_file: "logs/pm2-dropzone-error.log",
      out_file:   "logs/pm2-dropzone-out.log",
      log_date_format: "YYYY-MM-DD HH:mm:ss",
    },
  ],
};
