while ($true) {
    try {
        $p = Start-Process "node" -ArgumentList "server.js" -WorkingDirectory "E:\basit-jarvis-ai" -PassThru -NoNewWindow
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Started node PID $($p.Id)"
        $p.WaitForExit()
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Node exited with code $($p.ExitCode). Restarting in 3s..."
    } catch {
        Write-Host "Error: $_"
    }
    Start-Sleep 3
}
