param([string]$Base = "http://localhost:8083")
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root
$env:PYTHONPATH = $null

py -3.13 scripts/demo_offline.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

try {
    $body = @{
        tenantId       = "tenant_a"
        idempotencyKey = "demo-key-1"
        equipmentType  = "sprayer"
        areaHa         = 12.5
    } | ConvertTo-Json -Compress
    $r = Invoke-RestMethod -Uri "$Base/api/v1/applications" -Method Post -ContentType "application/json" -Body $body -TimeoutSec 10
    Write-Host "`n=== live application ===" -ForegroundColor Cyan
    $r | ConvertTo-Json -Depth 5
} catch {
    Write-Host "Live API skip (boot not running? $_)" -ForegroundColor Yellow
}
exit 0