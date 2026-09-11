@echo off
title Basit Jarvis AI - Remote PC Agent
color 0b
echo =========================================================
echo   ?? BASIT JARVIS AI ? ONE-CLICK UNIVERSAL AGENT
echo   Connecting this PC to Basit Jarvis Sovereign Network...
echo =========================================================
echo.
powershell -ExecutionPolicy Bypass -NoProfile -Command "$ErrorActionPreference = 'Stop'; try { $hub = (Get-Content '%~dp0server_url.txt' -ErrorAction SilentlyContinue); if (!$hub) { $hub = 'http://localhost:8888' }; Write-Host 'Connecting to:' $hub; Invoke-Expression (Invoke-RestMethod -Uri \"$hub/agent.ps1\") } catch { Write-Host 'Error:' $_.Exception.Message -ForegroundColor Red; pause }"
pause
