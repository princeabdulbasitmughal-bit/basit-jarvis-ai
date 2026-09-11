@echo off
title 👑 Basit Jarvis AI Desktop
cd /d "%~dp0"
if exist "BasitJarvisDesktop.exe" (
    start "" "BasitJarvisDesktop.exe"
    exit /b
)
if exist "..\desktop\BasitJarvisDesktop.exe" (
    start "" "..\desktop\BasitJarvisDesktop.exe"
    exit /b
)
echo [JARVIS]: Downloading latest BasitJarvisDesktop.exe...
powershell -Command "Invoke-WebRequest -Uri 'http://10.25.32.23:8888/BasitJarvisDesktop.exe' -OutFile 'BasitJarvisDesktop.exe'"
if exist "BasitJarvisDesktop.exe" (
    start "" "BasitJarvisDesktop.exe"
) else (
    echo Error: Could not launch BasitJarvisDesktop.exe
    pause
)
