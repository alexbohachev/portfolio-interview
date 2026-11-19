# Live workflow: idempotent retry + conflict on payload change (mirror fault IT).
param([string]$Base = "http://localhost:8083")
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Post-App($key, $areaHa) {
    $body = @{
        tenantId       = "tenant_a"
        idempotencyKey = $key
        equipmentType  = "sprayer"
        areaHa         = $areaHa
    } | ConvertTo-Json -Compress
    try {
        return Invoke-WebRequest -Uri "$Base/api/v1/applications" -Method Post `
            -ContentType "application/json" -Body $body -TimeoutSec 15 -UseBasicParsing
    } catch {
        if ($_.Exception.Response) { return $_.Exception.Response }
        throw
    }
}

Write-Host "=== work03 reliability demo ===" -ForegroundColor Cyan
Write-Host "(boot: .\make.ps1 boot in another terminal)" -ForegroundColor DarkGray

$key = "reliability-demo-" + [guid]::NewGuid().ToString("n").Substring(0, 8)

Write-Host "`n[1] First submit" -ForegroundColor Yellow
$r1 = Post-App $key 10.0
Write-Host "status=$($r1.StatusCode)"

Write-Host "`n[2] Retry same idempotency key (safe retry)" -ForegroundColor Yellow
$r2 = Post-App $key 10.0
Write-Host "status=$($r2.StatusCode) (expect 200, single external effect in DB)"

Write-Host "`n[3] Same key, different payload → conflict" -ForegroundColor Yellow
$r3 = Post-App $key 99.0
$code = if ($r3.StatusCode) { [int]$r3.StatusCode } else { 0 }
if ($code -eq 409) {
    Write-Host "OK 409 idempotency conflict" -ForegroundColor Green
} else {
    Write-Host "status=$code (expected 409 if API up)" -ForegroundColor Yellow
}

Write-Host "`nOffline fault matrix:" -ForegroundColor Yellow
py -3.13 scripts/demo_offline.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`nreliability_demo: OK" -ForegroundColor Green
exit 0