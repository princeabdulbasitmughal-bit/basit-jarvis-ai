# ===============================================================================
# 👑 BASIT JARVIS AI — UNIVERSAL REMOTE AGENT
# Run on ANY Windows PC / Laptop to enable 100% remote autonomous control
# Usage: powershell -ExecutionPolicy Bypass -File agent.ps1 -ServerUrl "https://..."
# Or 1-line: irm https://<your-jarvis-url>/agent.ps1 | iex
# ===============================================================================

param (
    [string]$ServerUrl = "SERVER_URL_PLACEHOLDER",
    [string]$NodeName = $env:COMPUTERNAME
)

$Host.UI.RawUI.WindowTitle = "👑 Basit Jarvis Remote Agent — $NodeName"

# Auto-generate or reuse NodeId
$IdFile = "$env:TEMP\jarvis_node_id.txt"
if (Test-Path $IdFile) {
    $NodeId = Get-Content $IdFile -Raw
    $NodeId = $NodeId.Trim()
} else {
    $NodeId = [System.Guid]::NewGuid().ToString().Substring(0,8)
    Set-Content $IdFile $NodeId
}

$OsVersion = [System.Environment]::OSVersion.VersionString
$UserName = $env:USERNAME

Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "  👑 BASIT JARVIS AI — UNIVERSAL REMOTE NODE     " -ForegroundColor Yellow
Write-Host "  Machine Name : $NodeName                       " -ForegroundColor Green
Write-Host "  Node ID      : $NodeId                         " -ForegroundColor Green
Write-Host "  Jarvis Server: $ServerUrl                      " -ForegroundColor White
Write-Host "=================================================" -ForegroundColor Cyan

# 1. Register with Jarvis Server
function Register-JarvisNode {
    $payload = @{
        id = $NodeId
        name = $NodeName
        user = $UserName
        os = $OsVersion
        platform = "win32"
    } | ConvertTo-Json

    try {
        $res = Invoke-RestMethod -Uri "$ServerUrl/api/nodes/register" -Method Post -Body $payload -ContentType "application/json" -TimeoutSec 8
        Write-Host "✅ [LINKED]: Connected to Basit Jarvis Sovereign Network!" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "⚠️ [CONNECTING]: Server unreachable at $ServerUrl, retrying..." -ForegroundColor Yellow
        return $false
    }
}

Register-JarvisNode | Out-Null

Write-Host "`n📡 Listening for remote commands from Basit bhai..." -ForegroundColor Cyan

# 2. Command Processing Loop
while ($true) {
    try {
        $pollUri = "$ServerUrl/api/nodes/poll?nodeId=$NodeId"
        $poll = Invoke-RestMethod -Uri $pollUri -TimeoutSec 6

        if ($poll.commands -and $poll.commands.Count -gt 0) {
            foreach ($cmd in $poll.commands) {
                $cmdId = $cmd.id
                $action = $cmd.action
                $param = $cmd.param
                $now = Get-Date -Format "HH:mm:ss"
                Write-Host "[$now] ⚡ COMMAND: $action" -ForegroundColor Magenta
                
                $resultText = "Success"

                switch ($action) {
                    "open_url" {
                        Start-Process $param
                        $resultText = "Opened URL: $param"
                    }
                    "open_app" {
                        Start-Process $param -ErrorAction SilentlyContinue
                        $resultText = "Launched app: $param"
                    }
                    "close_app" {
                        Stop-Process -Name $param -Force -ErrorAction SilentlyContinue
                        $resultText = "Closed app: $param"
                    }
                    "run_ps" {
                        $out = Invoke-Expression $param 2>&1 | Out-String
                        $resultText = $out.Trim()
                    }
                    "type_text" {
                        Add-Type -AssemblyName System.Windows.Forms
                        [System.Windows.Forms.SendKeys]::SendWait($param)
                        $resultText = "Typed text on screen"
                    }
                    "press_key" {
                        Add-Type -AssemblyName System.Windows.Forms
                        [System.Windows.Forms.SendKeys]::SendWait("{$param}")
                        $resultText = "Pressed key: $param"
                    }
                    "hotkey" {
                        Add-Type -AssemblyName System.Windows.Forms
                        [System.Windows.Forms.SendKeys]::SendWait($param)
                        $resultText = "Executed hotkey: $param"
                    }
                    "lock" {
                        rundll32.exe user32.dll,LockWorkStation
                        $resultText = "Workstation locked"
                    }
                    "mute" {
                        $w = New-Object -ComObject WScript.Shell
                        $w.SendKeys([char]173)
                        $resultText = "Toggled mute"
                    }
                    "vol_up" {
                        $w = New-Object -ComObject WScript.Shell
                        $w.SendKeys([char]175)
                        $resultText = "Volume increased"
                    }
                    "vol_down" {
                        $w = New-Object -ComObject WScript.Shell
                        $w.SendKeys([char]174)
                        $resultText = "Volume decreased"
                    }
                    "screenshot" {
                        try {
                            Add-Type -AssemblyName System.Drawing
                            Add-Type -AssemblyName System.Windows.Forms
                            $bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
                            $bmp = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
                            $g = [System.Drawing.Graphics]::FromImage($bmp)
                            $g.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)
                            $ms = New-Object System.IO.MemoryStream
                            $bmp.Save($ms, [System.Drawing.Imaging.ImageFormat]::Jpeg)
                            $b64 = [Convert]::ToBase64String($ms.ToArray())
                            $g.Dispose(); $bmp.Dispose(); $ms.Dispose()
                            $resultText = "SCREENSHOT_B64:$b64"
                        } catch {
                            $resultText = "Screenshot failed: $_"
                        }
                    }
                    "whatsapp" {
                        # Auto open chat and send
                        Start-Process $param
                        Start-Sleep -Seconds 5
                        Add-Type -AssemblyName System.Windows.Forms
                        [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
                        $resultText = "WhatsApp message dispatched"
                    }
                    default {
                        $resultText = "Unknown action: $action"
                    }
                }

                # Send execution result back to Jarvis Hub
                try {
                    $resPayload = @{
                        nodeId = $NodeId
                        cmdId = $cmdId
                        status = "SUCCESS"
                        result = $resultText
                    } | ConvertTo-Json

                    Invoke-RestMethod -Uri "$ServerUrl/api/nodes/result" -Method Post -Body $resPayload -ContentType "application/json" -TimeoutSec 4 | Out-Null
                } catch {}
            }
        }
    } catch {
        # Network transient error
    }
    Start-Sleep -Milliseconds 700
}
