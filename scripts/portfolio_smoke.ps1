param(
    [switch]$Strict
)
. "$PSScriptRoot\Get-RepoRoot.ps1"
$Root = Get-RepoRoot
$fail = 0

function Step($name, [scriptblock]$fn, [switch]$Optional) {
    Write-Host "`n>> $name" -ForegroundColor Cyan
    Push-Location $Root
    try {
        & $fn
        if ($LASTEXITCODE -ne 0 -and $null -ne $LASTEXITCODE) { throw "exit $LASTEXITCODE" }
        Write-Host "OK $name" -ForegroundColor Green
    } catch {
        if ($Optional -and -not $Strict) {
            Write-Host "SKIP $name : $_" -ForegroundColor Yellow
        } else {
            Write-Host "FAIL $name : $_" -ForegroundColor Red
            $script:fail++
        }
    } finally {
        Set-Location $Root
    }
}

Step "work01 demo offline" {
    Set-Location "$Root\work01-bank-marketing"
    $env:PYTHONPATH = "$Root\work01-bank-marketing\src"
    py -3.13 scripts/demo_offline.py
}

Step "work02 demo offline" {
    Set-Location "$Root\work02-rag-citations"
    $env:PYTHONPATH = "$Root\work02-rag-citations\src"
    py -3.13 scripts/demo_offline.py
}

Step "work03 demo offline" {
    Set-Location "$Root\work03-agent-workflow"
    py -3.13 scripts/demo_offline.py
}

Step "work04 demo offline" {
    Set-Location "$Root\work04-ml-serving"
    $env:PYTHONPATH = "$Root\work04-ml-serving\src"
    py -3.13 scripts/demo_offline.py
}

Step "work06 pytest (fast)" -Optional {
    Set-Location "$Root\work06-bible-rag"
    $env:PYTHONPATH = "$Root\work06-bible-rag\src"
    py -3.13 -m pytest -q tests/test_generate.py tests/test_db.py
}

Step "work07 demo offline" {
    Set-Location "$Root\work07-ai-platform"
    py -3.13 scripts/demo_offline.py
}

Step "work08 demo offline" {
    Set-Location "$Root\work08-demand-forecasting"
    $env:PYTHONPATH = "$Root\work08-demand-forecasting\src"
    py -3.13 scripts/demo_offline.py
}

Step "work05 docker smoke" -Optional {
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { throw "no docker" }
    Set-Location "$Root\work05-docguard"
    $ps = docker compose ps --status running 2>$null
    if (-not $ps) { throw "compose not running (run: cd work05-docguard; docker compose up -d)" }
    & "$Root\work05-docguard\scripts\smoke.ps1"
}

if ($fail -gt 0) {
    Write-Host "`nportfolio_smoke: $fail failure(s)" -ForegroundColor Red
    exit 1
}
Write-Host "`nPortfolio smoke: OK" -ForegroundColor Green
exit 0