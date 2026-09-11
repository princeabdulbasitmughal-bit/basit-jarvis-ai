$bin = "E:\basit-jarvis-ai\bin\cloudflared.exe"
$proc = Start-Process -FilePath $bin -ArgumentList "tunnel --url http://127.0.0.1:8888" -PassThru -NoNewWindow -RedirectStandardError "E:\basit-jarvis-ai\tunnel_err.log" -RedirectStandardOutput "E:\basit-jarvis-ai\tunnel_out.log"

$found = $null
for ($i = 0; $i -lt 25; $i++) {
    Start-Sleep -Seconds 1
    if (Test-Path "E:\basit-jarvis-ai\tunnel_err.log") {
        $content = Get-Content "E:\basit-jarvis-ai\tunnel_err.log" -Raw
        if ($content -match '(https://[a-zA-Z0-9-]+\.trycloudflare\.com)') {
            $found = $matches[1]
            break
        }
    }
}

if ($found) {
    Write-Host "CLOUDFLARE_URL: $found"
} else {
    Write-Host "NOT_CONNECTED_YET"
    if (Test-Path "E:\basit-jarvis-ai\tunnel_err.log") {
        Get-Content "E:\basit-jarvis-ai\tunnel_err.log" | Select-Object -Last 10
    }
}
