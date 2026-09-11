@echo off
title 👑 BASIT JARVIS AI — FULL SYSTEM MASTER LAUNCHER
color 0b
cd /d "E:\basit-jarvis-ai"
cls

echo ===============================================================================
echo   👑 BASIT JARVIS AI — SOVEREIGN PC CONTROLLER & AUTONOMOUS AI OS 👑
echo ===============================================================================
echo.

:: Detect Python executable
set "PY_EXE=python"
where python >nul 2>&1
if %errorlevel% neq 0 (
    where py >nul 2>&1
    if %errorlevel% equ 0 (
        set "PY_EXE=py"
    ) else (
        if exist "C:\Users\absh5\AppData\Local\Programs\Python\Python311\python.exe" (
            set "PY_EXE=C:\Users\absh5\AppData\Local\Programs\Python\Python311\python.exe"
        )
    )
)

echo [1/3] Starting Background Web Server & REST API on port 8888...
start "Basit Jarvis API Server" /min "%PY_EXE%" server.py
timeout /t 3 >nul

echo [2/3] Opening Cyberpunk Web Control HUD in browser...
start http://localhost:8888

echo [3/3] Starting Real-Time Voice Assistant Engine...
echo.
echo ===============================================================================
echo   🎙️ WAKE WORDS: "Hey Jarvis" OR "Basit"
echo   ⌨️ HOTKEY:      [CTRL + SHIFT + J]
echo   🌐 DASHBOARD:   http://localhost:8888
echo.
echo   VOICE COMMAND EXAMPLES (Urdu & English):
echo     - "Chrome kholo" / "VS Code band karo"
echo     - "Awaz 80 kardo" / "Awaz barhao" / "Awaz band kardo"
echo     - "Desktop dikhao" / "Screenshot lo" / "PC lock kardo"
echo     - "Downloads folder kholo" / "Git status check karo"
echo     - "Generate viral hooks for WhatsApp Marketing"
echo     - "Write a 45 second script for that topic"
echo     - "Start content mode" / "Start coding mode"
echo     - "/basit1 create a python fastapi server"
echo     - "/basit2 research latest frontier AI models"
echo     - "/basit3 sweep zombies and check security"
echo     - "/basitloop build an analytics dashboard"
echo ===============================================================================
echo.

"%PY_EXE%" jarvis.py
pause
