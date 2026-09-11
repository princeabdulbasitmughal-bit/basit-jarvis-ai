@echo off
title 👑 BASIT JARVIS AI — SERVER (PORT 8888)
color 0a
cd /d "E:\basit-jarvis-ai"

echo ===============================================================================
echo   👑 BASIT JARVIS AI — LAUNCHING WEB HUD & REST API (PORT 8888)
echo ===============================================================================
echo.
echo Dashboard URL: http://127.0.0.1:8888
echo Swagger Docs:  http://127.0.0.1:8888/docs
echo.
echo Starting Uvicorn server on port 8888...
echo.

python -m uvicorn server:app --host 0.0.0.0 --port 8888
if %errorlevel% neq 0 (
    py -m uvicorn server:app --host 0.0.0.0 --port 8888
)
if %errorlevel% neq 0 (
    "C:\Users\absh5\AppData\Local\Programs\Python\Python311\python.exe" -m uvicorn server:app --host 0.0.0.0 --port 8888
)

pause
