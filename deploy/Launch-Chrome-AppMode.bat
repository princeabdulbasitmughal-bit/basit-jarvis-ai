@echo off
title Launch Basit Jarvis in Chrome App Mode
cd /d "%~dp0"

echo [JARVIS]: Launching Basit Jarvis in Native App Window (Zero "Not Secure" warnings)...

:: Check for Google Chrome
where chrome.exe >nul 2>nul
if %errorlevel% equ 0 (
    start "" chrome.exe --app="http://10.25.32.23:8888" --unsafely-treat-insecure-origin-as-secure="http://10.25.32.23:8888" --user-data-dir="%TEMP%\JarvisChromeProfile"
    exit /b
)

:: Check Chrome in standard Program Files
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --app="http://10.25.32.23:8888" --unsafely-treat-insecure-origin-as-secure="http://10.25.32.23:8888" --user-data-dir="%TEMP%\JarvisChromeProfile"
    exit /b
)

:: Fallback to Microsoft Edge (Pre-installed on every Windows 10/11)
if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
    start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --app="http://10.25.32.23:8888" --unsafely-treat-insecure-origin-as-secure="http://10.25.32.23:8888" --user-data-dir="%TEMP%\JarvisEdgeProfile"
    exit /b
)

:: Generic launch
start http://10.25.32.23:8888
