# Підняти live-стенди для запису (Docker / API). Запускайте окремі термінали за підказками.
param(
    [ValidateSet("work05", "work07", "work06", "work03", "status")]
    [string]$Target = "status"
)
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$ErrorActionPreference = "Stop"

function Show-Status {
    Write-Host "=== Live status ===" -ForegroundColor Cyan
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
        Set-Location "$Root\work05-docguard"
        docker compose up -d --build
        Start-Sleep 15
        & ".\make.ps1" demo
        exit $LASTEXITCODE
    }
    "work07" {
        Set-Location "$Root\work07-ai-platform"
        Write-Host "work07: зазвичай 2–5 хв build + 90s warm-up для rag-api"
        & ".\make.ps1" up
        Start-Sleep 90
        & ".\make.ps1" smoke
        & ".\scripts\demo.ps1"
        exit $LASTEXITCODE
    }
    "work06" {
        Set-Location "$Root\work06-bible-rag"
        $env:PYTHONPATH = "$Root\work06-bible-rag\src"
        Write-Host "Запусти в іншому вікні: .\make.ps1 serve"
        Start-Sleep 3
        & ".\make.ps1" demo
        exit $LASTEXITCODE
    }
    "work03" {
        Set-Location "$Root\work03-agent-workflow"
        docker compose up -d
        Write-Host "Запусти в іншому вікні: .\make.ps1 boot"
        & ".\scripts\demo.ps1"
        exit 0
    }
}