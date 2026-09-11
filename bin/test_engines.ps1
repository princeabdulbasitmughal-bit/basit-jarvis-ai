$routes = @('basit1','basit2','basit3','basit4','basitswarm','arsenal')
foreach ($r in $routes) {
    try {
        $res = Invoke-RestMethod -Uri "http://localhost:8888/api/$r" -Method POST -ContentType 'application/json' -Body '{}'
        Write-Host "ROUTE /api/$r => SUCCESS: $($res.success) - ENGINE: $($res.engine)"
    } catch {
        Write-Host "ROUTE /api/$r => ERROR: $($_.Exception.Message)"
    }
}
