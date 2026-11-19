param(
    [ValidateSet("work05", "work07", "work06", "work03", "status")]
    [string]$Target = "status"
)
. "$PSScriptRoot\Get-RepoRoot.ps1"
$Root = Get-RepoRoot
$ErrorActionPreference = "Stop"

function Show-Status {
    Write-Host "=== Live status (repo: $Root) ===" -ForegroundColor Cyan
    foreach ($p in @(8095, 8096, 8097, 8098, 8083, 8090, 8084, 8082)) {
        try {
            $r = Invoke-WebRequest -Uri "http://127.0.0.1:${p}/health" -TimeoutSec 2 -UseBasicParsing
            Write-Host "OK :$p $($r.StatusCode)" -ForegroundColor Green
        } catch {
            Write-Host "-- :$p" -ForegroundColor DarkGray
        }
    }
}

switch ($Target) {
    "status" { Show-Status; exit 0 }
    "work05" {
        Set-Location (Join-Path $Root "work05-docguard")
        docker compose up -d --build
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        Start-Sleep 15
        & ".\make.ps1" demo
        exit $LASTEXITCODE
    }
    "work07" {
        Set-Location (Join-Path $Root "work07-ai-platform")
        Write-Host "work07: build/up + 90s warm-up rag-api"
        & ".\make.ps1" build
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        & ".\make.ps1" up
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        Start-Sleep 90
        & ".\make.ps1" smoke
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        py -3.13 scripts/benchmark_latency.py
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        & ".\scripts\demo.ps1"
        exit $LASTEXITCODE
    }
    "work06" {
        Set-Location (Join-Path $Root "work06-bible-rag")
        $env:PYTHONPATH = Join-Path $Root "work06-bible-rag\src"
        Write-Host "Інший термінал: .\make.ps1 serve"
        & ".\make.ps1" demo
        exit $LASTEXITCODE
    }
    "work03" {
        Set-Location (Join-Path $Root "work03-agent-workflow")
        docker compose up -d
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        Write-Host "Інший термінал: .\make.ps1 boot"
        & ".\scripts\demo.ps1"
        exit $LASTEXITCODE
    }
}