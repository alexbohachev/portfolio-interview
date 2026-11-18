param([string]$Base = "http://127.0.0.1:8098")
$ErrorActionPreference = "Stop"

function Show($title, $obj) {
    Write-Host "`n=== $title ===" -ForegroundColor Cyan
    $obj | ConvertTo-Json -Depth 6
}

$h = Invoke-RestMethod -Uri "$Base/health" -TimeoutSec 5
Show "health" $h
if (-not $h.index_ready) { throw "index not ready — run .\make.ps1 all" }

$body1 = '{"question":"Що говорить вірш Gen.1.1 про творіння?","top_k":3,"use_llm":false}'
$r1 = Invoke-RestMethod -Uri "$Base/v1/ask" -Method Post -ContentType "application/json; charset=utf-8" `
    -Body ([System.Text.Encoding]::UTF8.GetBytes($body1))
Show "ask uk_ubk (default)" $r1

$body2 = '{"question":"Що говорить вірш Gen.1.1 про творіння?","translation_id":"en_kjv_stub","top_k":2}'
$r2 = Invoke-RestMethod -Uri "$Base/v1/ask" -Method Post -ContentType "application/json; charset=utf-8" `
    -Body ([System.Text.Encoding]::UTF8.GetBytes($body2))
Show "ask en_kjv_stub" $r2

Write-Host "`nГотово. UI: .\make.ps1 ui" -ForegroundColor Green