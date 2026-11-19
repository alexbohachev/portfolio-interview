# Усі offline-демо (1–7) перед співбесідою
param(
    [switch]$Strict
)
. "$PSScriptRoot\Get-RepoRoot.ps1"
$Root = Get-RepoRoot
$ErrorActionPreference = "Stop"
$failed = 0

$demos = @(
    @{ Name = "work01"; Path = "work01-bank-marketing"; Env = @{ PYTHONPATH = (Join-Path $Root "work01-bank-marketing\src") }; Script = "scripts/demo_offline.py" }
    @{ Name = "work02"; Path = "work02-rag-citations"; Env = @{ PYTHONPATH = (Join-Path $Root "work02-rag-citations\src") }; Script = "scripts/demo_offline.py" }
    @{ Name = "work03"; Path = "work03-agent-workflow"; Env = @{}; Script = "scripts/demo_offline.py" }
    @{ Name = "work04"; Path = "work04-ml-serving"; Env = @{ PYTHONPATH = (Join-Path $Root "work04-ml-serving\src") }; Script = "scripts/demo_offline.py" }
    @{ Name = "work06"; Path = "work06-bible-rag"; Env = @{ PYTHONPATH = (Join-Path $Root "work06-bible-rag\src") }; Pytest = @("tests/test_generate.py", "tests/test_db.py"); Optional = $true }
    @{ Name = "work07"; Path = "work07-ai-platform"; Env = @{}; Script = "scripts/demo_offline.py" }
)

Write-Host "=== Portfolio prep (offline) ===" -ForegroundColor Cyan
Write-Host "Root: $Root"

foreach ($d in $demos) {
    Write-Host "`n--- $($d.Name) ---" -ForegroundColor Yellow
    $wd = Join-Path $Root $d.Path
    if (-not (Test-Path $wd)) {
        Write-Host "FAIL missing $wd" -ForegroundColor Red
        $failed++
        continue
    }
    Push-Location $wd
  try {
        foreach ($k in $d.Env.Keys) { Set-Item -Path "env:$k" -Value $d.Env[$k] }
        if ($d.Script) {
            py -3.13 $d.Script
            if ($LASTEXITCODE -ne 0) { throw "exit $LASTEXITCODE" }
        } elseif ($d.Pytest) {
            py -3.13 -m pytest -q @($d.Pytest)
            if ($LASTEXITCODE -ne 0) { throw "exit $LASTEXITCODE" }
        }
        Write-Host "OK $($d.Name)" -ForegroundColor Green
    } catch {
        if ($d.Optional -and -not $Strict) {
            Write-Host "SKIP $($d.Name): $_" -ForegroundColor Yellow
        } else {
            Write-Host "FAIL $($d.Name): $_" -ForegroundColor Red
            $failed++
        }
    } finally {
        Pop-Location
    }
}

Set-Location $Root
$smokeLabel = if ($Strict) { "strict" } else { "optional docker" }
Write-Host "`n=== portfolio_smoke ($smokeLabel) ===" -ForegroundColor Cyan
if ($Strict) {
    & "$Root\scripts\portfolio_smoke.ps1" -Strict
} else {
    & "$Root\scripts\portfolio_smoke.ps1"
}
if ($LASTEXITCODE -ne 0) { $failed++ }

if ($failed -gt 0) {
    Write-Host "`nprep_interview: $failed failure(s)" -ForegroundColor Red
    exit 1
}
Write-Host "`nprep_interview: OK" -ForegroundColor Green
exit 0