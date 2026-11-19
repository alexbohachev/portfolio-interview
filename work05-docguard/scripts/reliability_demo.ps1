# Live DocGuard: tenant isolation, ACL cache invalidation, retrieval down → degraded.
param(
    [string]$Gateway = "http://localhost:8096"
)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Query-DocGuard($tenant, $principal, $question) {
    $headers = @{ "X-Tenant-Id" = $tenant; "X-Principal-Id" = $principal }
    $body = (@{ question = $question } | ConvertTo-Json -Compress)
    Invoke-RestMethod -Uri "$Gateway/api/v1/query" -Method Post -Headers $headers `
        -ContentType "application/json; charset=utf-8" `
        -Body ([System.Text.Encoding]::UTF8.GetBytes($body))
}

Write-Host "=== work05 reliability demo ===" -ForegroundColor Cyan

Write-Host "`n[1] Tenant A (alice)" -ForegroundColor Yellow
$a = Query-DocGuard "tenant_a" "alice" "бура іржа пшениця"
Write-Host "hits=$($a.hits.Count) first=$($a.hits[0].doc_id)"

Write-Host "`n[2] Tenant B (carol) — інший ACL / корпус" -ForegroundColor Yellow
$b = Query-DocGuard "tenant_b" "carol" "економічний поріг шкідників IPM"
Write-Host "hits=$($b.hits.Count) first=$($b.hits[0].doc_id)"

Write-Host "`n[3] Invalidate cache (carol) + repeat" -ForegroundColor Yellow
$ih = @{ "X-Tenant-Id" = "tenant_b"; "X-Principal-Id" = "carol" }
Invoke-RestMethod -Uri "$Gateway/api/v1/admin/invalidate-cache" -Method Post -Headers $ih | Out-Null
$b2 = Query-DocGuard "tenant_b" "carol" "економічний поріг шкідників IPM"
Write-Host "hits after invalidate=$($b2.hits.Count)"

Write-Host "`n[4] Stop retrieval container → degraded" -ForegroundColor Yellow
docker compose stop retrieval | Out-Null
Start-Sleep 3
try {
    $d = Query-DocGuard "tenant_a" "alice" "test degraded"
    if ($d.degraded) {
        Write-Host "OK degraded=true mode=$($d.mode)" -ForegroundColor Green
    } else {
        throw "expected degraded=true"
    }
} finally {
    docker compose start retrieval | Out-Null
    Start-Sleep 8
}

Write-Host "`nreliability_demo: OK" -ForegroundColor Green
exit 0