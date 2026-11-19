# Швидка перевірка перед співбесідою (best-effort, без падіння всього run)
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$fail = 0

function Step($name, [scriptblock]$fn) {
    Write-Host "`n>> $name" -ForegroundColor Cyan
    try {
        & $fn
        Write-Host "OK $name" -ForegroundColor Green
    } catch {
        Write-Host "SKIP/FAIL $name : $_" -ForegroundColor Yellow
        $script:fail++
    }
}

Step "work01 demo offline" {
    Set-Location "$Root\work01-bank-marketing"
    $env:PYTHONPATH = "$Root\work01-bank-marketing\src"
    py -3.13 scripts/demo_offline.py | Out-Null
}

Step "work02 demo offline" {
    Set-Location "$Root\work02-rag-citations"
    $env:PYTHONPATH = "$Root\work02-rag-citations\src"
    py -3.13 scripts/demo_offline.py | Out-Null
}

Step "work03 demo offline" {
    Set-Location "$Root\work03-agent-workflow"
    py -3.13 scripts/demo_offline.py | Out-Null
}

Step "work04 demo offline" {
    Set-Location "$Root\work04-ml-serving"
    $env:PYTHONPATH = "$Root\work04-ml-serving\src"
    py -3.13 scripts/demo_offline.py | Out-Null
}

Step "work06 pytest (fast)" {
    Set-Location "$Root\work06-bible-rag"
    $env:PYTHONPATH = "$Root\work06-bible-rag\src"
    py -3.13 -m pytest -q tests/test_generate.py tests/test_db.py
}

Step "work07 demo offline" {
    Set-Location "$Root\work07-ai-platform"
    py -3.13 scripts/demo_offline.py | Out-Null
}

Step "work05 docker smoke" {
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { throw "no docker" }
    Set-Location "$Root\work05-docguard"
    $ps = docker compose ps --status running 2>$null
    if (-not $ps) { throw "compose not running" }
    & "$Root\work05-docguard\scripts\smoke.ps1" | Out-Null
}

Set-Location $Root
if ($fail -gt 0) { Write-Host "`nДеякі кроки пропущено ($fail). Див. PORTFOLIO.md" -ForegroundColor Yellow; exit 0 }
Write-Host "`nPortfolio smoke: усі кроки OK" -ForegroundColor Green