@echo off
title Basit Jarvis AI - Cloudflare Global Tunnel
color 0b
echo ===============================================================================
echo   👑 BASIT JARVIS AI — CLOUDFLARE SECURE GLOBAL TUNNEL
echo   Connecting localhost:8888 to Cloudflare Worldwide Network...
echo ===============================================================================
echo.
if not exist "%~dp0bin\cloudflared.exe" (
    echo [ERROR] cloudflared.exe not found in %~dp0bin!
    pause
    exit /b 1
)

"%~dp0bin\cloudflared.exe" tunnel --url http://127.0.0.1:8888
pause
