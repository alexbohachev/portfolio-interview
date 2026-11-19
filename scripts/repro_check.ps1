# Перевірка відтворюваності з чистого клону (offline обов'язково; docker — опційно).
param(
    [switch]$Docker
)
. "$PSScriptRoot\Get-RepoRoot.ps1"
$Root = Get-RepoRoot
$failed = 0

Write-Host "repro_check: $Root" -ForegroundColor Cyan

& "$Root\scripts\prep_interview.ps1"
if ($LASTEXITCODE -ne 0) { $failed++ }

if ($Docker) {
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Host "FAIL: -Docker set but docker missing" -ForegroundColor Red
        exit 1
    }
    Push-Location (Join-Path $Root "work05-docguard")
    try {
        docker compose up -d --build
        if ($LASTEXITCODE -ne 0) { throw "work05 compose" }
        Start-Sleep 20
        & ".\scripts\smoke.ps1"
        if ($LASTEXITCODE -ne 0) { throw "work05 smoke" }
        Write-Host "OK work05 docker smoke" -ForegroundColor Green
    } catch {
        Write-Host "FAIL work05: $_" -ForegroundColor Red
        $failed++
    } finally {
        Pop-Location
    }

    Push-Location (Join-Path $Root "work07-ai-platform")
    try {
        & ".\make.ps1" build
        & ".\make.ps1" up
        Start-Sleep 90
        py -3.13 scripts/smoke_test.py
        if ($LASTEXITCODE -ne 0) { throw "work07 smoke" }
        py -3.13 scripts/benchmark_latency.py
        if ($LASTEXITCODE -ne 0) { throw "work07 bench" }
        Write-Host "OK work07 docker smoke+bench" -ForegroundColor Green
    } catch {
        Write-Host "FAIL work07: $_" -ForegroundColor Red
        $failed++
    } finally {
        Pop-Location
    }
}

if ($failed -gt 0) { exit 1 }
Write-Host "repro_check: OK" -ForegroundColor Green
exit 0