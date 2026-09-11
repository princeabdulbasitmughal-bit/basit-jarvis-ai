while ($true) {
    try {
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Starting localtunnel..."
        $pinfo = New-Object System.Diagnostics.ProcessStartInfo
        $pinfo.FileName = "cmd"
        $pinfo.Arguments = "/c lt --port 8888 --subdomain basit-jarvis 2>&1"
        $pinfo.UseShellExecute = $false
        $pinfo.RedirectStandardOutput = $true
        $pinfo.CreateNoWindow = $true
        $p = [System.Diagnostics.Process]::Start($pinfo)
        while (!$p.StandardOutput.EndOfStream) {
            $line = $p.StandardOutput.ReadLine()
            Write-Host $line
            if ($line -match "your url is: (.+)") {
                $url = $matches[1].Trim()
                Set-Content "E:\basit-jarvis-ai\logs\tunnel-url.txt" $url
                Write-Host "TUNNEL URL: $url" -ForegroundColor Green
            }
        }
        $p.WaitForExit()
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Tunnel died. Restarting in 5s..."
    } catch { Write-Host "Error: $_" }
    Start-Sleep 5
}
