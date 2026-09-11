@echo off
title Basit Jarvis AI — Voice Assistant
color 0b
echo ========================================================
echo   👑 BASIT JARVIS AI — VOICE ASSISTANT 👑
echo ========================================================
echo.
echo Wake words: "Hey Jarvis" or "Basit"
echo Fallback Hotkey: [CTRL + SHIFT + J]
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

"%PY_EXE%" jarvis.py
pause
