@echo off
title 👑 BASIT JARVIS AI — SERVER (PORT 8888)
color 0b
cd /d "E:\basit-jarvis-ai"

echo ===============================================================================
echo   👑 BASIT JARVIS AI — REST API & WEB HUD (Port 8888)
echo ===============================================================================
echo.
echo Starting Web Server on http://127.0.0.1:8888 ...
echo.

:: 1. Try python directly
where python >nul 2>&1
if %errorlevel% equ 0 (
    python server.py
    goto end
)

:: 2. Try py launcher
where py >nul 2>&1
if %errorlevel% equ 0 (
    py server.py
    goto end
)

:: 3. Try known Python 3.11 absolute path
if exist "C:\Users\absh5\AppData\Local\Programs\Python\Python311\python.exe" (
    "C:\Users\absh5\AppData\Local\Programs\Python\Python311\python.exe" server.py
    goto end
)

echo [ERROR] Python not found on PATH or in standard directory!
:end
pause
