@echo off
title 👑 BASIT JARVIS AI — SERVER LAUNCHER & DIAGNOSTIC
color 0b
cd /d "E:\basit-jarvis-ai"

echo ===============================================================================
echo   👑 BASIT JARVIS AI — DIAGNOSTIC & INSTANT LAUNCHER
echo ===============================================================================
echo.

:: Detect Python executable
set "PY_BIN=python"
where python >nul 2>&1
if %errorlevel% neq 0 (
    where py >nul 2>&1
    if %errorlevel% equ 0 (
        set "PY_BIN=py"
    ) else (
        if exist "C:\Users\absh5\AppData\Local\Programs\Python\Python311\python.exe" (
            set "PY_BIN=C:\Users\absh5\AppData\Local\Programs\Python\Python311\python.exe"
        )
    )
)

echo [1/3] Python Detected: %PY_BIN%
"%PY_BIN%" --version

echo.
echo [2/3] Verifying FastAPI & Uvicorn libraries...
"%PY_BIN%" -c "import fastapi, uvicorn; print('    -> FastAPI & Uvicorn: OK')"

echo.
echo [3/3] Starting Basit Jarvis Server on Port 8888...
echo ===============================================================================
echo   🌐 Web Dashboard: http://127.0.0.1:8888
echo   📖 API Docs:      http://127.0.0.1:8888/docs
echo ===============================================================================
echo.
echo (Keep this window open while using Jarvis)
echo.

"%PY_BIN%" -m uvicorn server:app --host 0.0.0.0 --port 8888

echo.
echo [SERVER STOPPED]
pause
