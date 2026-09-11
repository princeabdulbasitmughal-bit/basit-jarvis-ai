@echo off
title Basit Jarvis AI — CLI Mode
color 0a
echo ========================================================
echo   👑 BASIT JARVIS AI — INTERACTIVE CLI 👑
echo ========================================================
echo.
echo Type your commands directly:
echo   - "show desktop"
echo   - "set volume to 80"
echo   - "start coding mode"
echo   - "open chrome and search cats"
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

"%PY_EXE%" jarvis.py --cli
pause
