$r1 = Invoke-RestMethod -Uri 'http://localhost:8888/api/command' -Method POST -ContentType 'application/json' -Body '{"command":"mute"}'
Write-Host "MUTE: $($r1.response)"

Start-Sleep -Seconds 1

$r2 = Invoke-RestMethod -Uri 'http://localhost:8888/api/command' -Method POST -ContentType 'application/json' -Body '{"command":"unmute"}'
Write-Host "UNMUTE: $($r2.response)"

Start-Sleep -Seconds 1

$r3 = Invoke-RestMethod -Uri 'http://localhost:8888/api/command' -Method POST -ContentType 'application/json' -Body '{"command":"volume 70"}'
Write-Host "VOLUME 70: $($r3.response)"

Start-Sleep -Seconds 1

$r4 = Invoke-RestMethod -Uri 'http://localhost:8888/api/command' -Method POST -ContentType 'application/json' -Body '{"command":"take a screenshot"}'
Write-Host "SCREENSHOT: $($r4.response)"
Write-Host "PATH: $($r4.path)"
