@echo off
title Basit Jarvis AI Server
cd /d E:\basit-jarvis-ai
echo =======================================
echo  BASIT JARVIS AI - AUTO-RESTART WATCHDOG
echo =======================================
:LOOP
echo [%TIME%] Starting server...
node server.js
echo [%TIME%] Server stopped. Restarting in 3s...
timeout /t 3 /nobreak >nul
goto LOOP
