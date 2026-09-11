Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  ♾️ BASIT JARVIS AI — 100% EXHAUSTIVE FEATURE VERIFIER" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

$base = "http://localhost:8888"
$passed = 0
$failed = 0

function Test-Endpoint($name, $url, $method = "GET", $body = $null) {
    try {
        $params = @{
            Uri = $url
            Method = $method
            TimeoutSec = 8
        }
        if ($body) {
            $params["ContentType"] = "application/json"
            $params["Body"] = ($body | ConvertTo-Json -Compress)
        }
        $res = Invoke-RestMethod @params
        Write-Host " [PASS] $name" -ForegroundColor Green
        $script:passed++
        return $res
    } catch {
        Write-Host " [FAIL] $name : $($_.Exception.Message)" -ForegroundColor Red
        $script:failed++
        return $null
    }
}

Write-Host "`n--- 1. CORE TELEMETRY & CLUSTER TESTS ---" -ForegroundColor White
Test-Endpoint "Server Status API" "$base/api/status"
Test-Endpoint "Cluster Telemetry API" "$base/api/cluster"

Write-Host "`n--- 2. DESKTOP OS AUDIO & SYSTEM TESTS ---" -ForegroundColor White
Test-Endpoint "Volume Set (80%)" "$base/api/command" "POST" @{ command = "volume 80" }
Test-Endpoint "Volume Up (+10%)" "$base/api/command" "POST" @{ command = "volume up" }
Test-Endpoint "Volume Down (-10%)" "$base/api/command" "POST" @{ command = "volume down" }
Test-Endpoint "Mute System Audio" "$base/api/command" "POST" @{ command = "mute" }
Test-Endpoint "Unmute System Audio" "$base/api/command" "POST" @{ command = "unmute" }
Test-Endpoint "Recycle Bin Empty" "$base/api/command" "POST" @{ command = "recycle bin khali karo" }
Test-Endpoint "System Specs Command" "$base/api/command" "POST" @{ command = "system specs batao" }

Write-Host "`n--- 3. SCREENSHOT & STATIC FILE SERVING TESTS ---" -ForegroundColor White
$scRes = Test-Endpoint "Screenshot Capture" "$base/api/command" "POST" @{ command = "take a screenshot" }
if ($scRes -and $scRes.path) {
    $filename = Split-Path $scRes.path -Leaf
    Test-Endpoint "Screenshot Static Serving (/screenshots/$filename)" "$base/screenshots/$filename"
}

Write-Host "`n--- 4. PRODUCTIVITY (NOTES & CLIPBOARD) TESTS ---" -ForegroundColor White
Test-Endpoint "Post Quick Note" "$base/api/notes" "POST" @{ text = "Automated test note from BasitLoop" }
Test-Endpoint "Get Stored Notes" "$base/api/notes"
Test-Endpoint "Get Clipboard" "$base/api/clipboard"

Write-Host "`n--- 5. ALL 6 BASIT AUTONOMOUS POWER ENGINES ---" -ForegroundColor White
$engines = @('basit1', 'basit2', 'basit3', 'basit4', 'basitswarm', 'arsenal')
foreach ($eng in $engines) {
    Test-Endpoint "Engine /$eng" "$base/api/$eng" "POST" @{ prompt = "Healthcheck test" }
}

Write-Host "`n==========================================================" -ForegroundColor Cyan
Write-Host "  TEST RESULTS: $passed PASSED | $failed FAILED" -ForegroundColor ($failed -eq 0 ? "Green" : "Red")
Write-Host "==========================================================" -ForegroundColor Cyan
