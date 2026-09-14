@echo off
title 👑 Basit Jarvis AI — PM2 Daemon Launcher
color 0B
echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║   👑  BASIT JARVIS AI — PM2 ENTERPRISE LAUNCHER          ║
echo  ║   24/7 Zero-Downtime with Auto-Restart                   ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.

cd /d E:\basit-jarvis-ai

:: Check if PM2 is installed
pm2 --version >nul 2>&1
if errorlevel 1 (
    echo [!] PM2 not found — installing now...
    npm install -g pm2
)

:: Check if server is already managed by PM2
pm2 describe jarvis-server >nul 2>&1
if errorlevel 1 (
    echo [+] Starting Jarvis with PM2 ecosystem...
    pm2 start ecosystem.config.js
) else (
    echo [*] Jarvis already running — restarting all processes...
    pm2 restart all
)

echo.
echo [+] PM2 Status:
pm2 status

echo.
echo [+] Saving PM2 config for auto-start on reboot...
pm2 save

echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║  ✅ Jarvis is LIVE on PM2!                               ║
echo  ║                                                          ║
echo  ║  Dashboard:  http://localhost:8888                       ║
echo  ║  Tunnel:     https://basit-jarvis.loca.lt                ║
echo  ║  LAN:        http://10.25.32.23:8888                     ║
echo  ║                                                          ║
echo  ║  Commands:                                               ║
echo  ║    pm2 status     — see all processes                    ║
echo  ║    pm2 logs       — live logs                            ║
echo  ║    pm2 restart all — restart everything                  ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.
pause
