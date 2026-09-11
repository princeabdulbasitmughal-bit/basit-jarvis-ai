$response = Invoke-RestMethod -Uri 'http://localhost:8888/api/command' -Method POST -ContentType 'application/json' -Body '{"command":"mute"}'
Write-Host "MUTE RESPONSE: $($response | ConvertTo-Json)"
