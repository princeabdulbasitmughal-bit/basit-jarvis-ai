# ============================================================
# BASIT JARVIS AI — Master Startup Script
# Run this once: powershell -ExecutionPolicy Bypass -File E:\basit-jarvis-ai\START-ALL.ps1
# Both server and tunnel will auto-restart forever
# ============================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  BASIT JARVIS AI - MASTER STARTUP" -ForegroundColor Yellow  
Write-Host "========================================" -ForegroundColor Cyan

# Kill any existing processes
Get-Process node -EA SilentlyContinue | Stop-Process -Force -EA SilentlyContinue
Get-Process -Name "cmd" -EA SilentlyContinue | Where-Object {$_.MainWindowTitle -like "*lt*"} | Stop-Process -Force -EA SilentlyContinue
Start-Sleep 1

Write-Host "[1/2] Starting Server Watchdog..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass -WindowStyle Hidden -File E:\basit-jarvis-ai\watchdog.ps1" -WindowStyle Hidden

Start-Sleep 4

Write-Host "[2/2] Starting Tunnel Watchdog..." -ForegroundColor Green  
Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass -WindowStyle Hidden -File E:\basit-jarvis-ai\watchdog-tunnel.ps1" -WindowStyle Hidden

Start-Sleep 6

# Show status
$node = Get-Process node -EA SilentlyContinue | Select-Object -First 1
if ($node) {
    Write-Host "`n✅ Server ONLINE (PID $($node.Id))" -ForegroundColor Green
    Write-Host "✅ Tunnel STARTING..." -ForegroundColor Green
    $lanIp = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -like "*Wi-Fi*" -or $_.InterfaceAlias -like "*Ethernet*" } | Where-Object { $_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.254.*" } | Select-Object -First 1).IPAddress
    if (!$lanIp) { $lanIp = "127.0.0.1" }
    Write-Host "`n  Local:  http://localhost:8888" -ForegroundColor Cyan
    Write-Host "  LAN:    http://$($lanIp):8888" -ForegroundColor Cyan
    $tunnelUrl = ""
    if (Test-Path "E:\basit-jarvis-ai\logs\tunnel-url.txt") {
        $tunnelUrl = (Get-Content "E:\basit-jarvis-ai\logs\tunnel-url.txt" -Raw).Trim()
    }
    if ($tunnelUrl) {
        Write-Host "  Global: $tunnelUrl" -ForegroundColor Green
    } else {
        Write-Host "  Global: check E:\basit-jarvis-ai\logs\tunnel.log" -ForegroundColor Cyan
    }
} else {
    Write-Host "⚠️  Server starting..." -ForegroundColor Yellow
}

Write-Host "`n✅ Both watchdogs running in background - DONE!" -ForegroundColor Green
