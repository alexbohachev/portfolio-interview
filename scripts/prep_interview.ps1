# Усі offline-демо (1–7) перед співбесідою — без Docker, крім опційного smoke
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$ErrorActionPreference = "Continue"

$demos = @(
    @{ Name = "work01"; Path = "work01-bank-marketing"; Env = @{ PYTHONPATH = "$Root\work01-bank-marketing\src" }; Script = "scripts/demo_offline.py" }
    @{ Name = "work02"; Path = "work02-rag-citations"; Env = @{ PYTHONPATH = "$Root\work02-rag-citations\src" }; Script = "scripts/demo_offline.py" }
    @{ Name = "work03"; Path = "work03-agent-workflow"; Env = @{}; Script = "scripts/demo_offline.py" }
    @{ Name = "work04"; Path = "work04-ml-serving"; Env = @{ PYTHONPATH = "$Root\work04-ml-serving\src" }; Script = "scripts/demo_offline.py" }
    @{ Name = "work06"; Path = "work06-bible-rag"; Env = @{ PYTHONPATH = "$Root\work06-bible-rag\src" }; Script = $null; Pytest = @("tests/test_generate.py", "tests/test_db.py") }
    @{ Name = "work07"; Path = "work07-ai-platform"; Env = @{}; Script = "scripts/demo_offline.py" }
)

Write-Host "=== Portfolio prep (offline) ===" -ForegroundColor Cyan
foreach ($d in $demos) {
    Write-Host "`n--- $($d.Name) ---" -ForegroundColor Yellow
    Set-Location (Join-Path $Root $d.Path)
    foreach ($k in $d.Env.Keys) { Set-Item -Path "env:$k" -Value $d.Env[$k] }
    if ($d.Script) {
        py -3.13 $d.Script
    } elseif ($d.Pytest) {
        py -3.13 -m pytest -q @($d.Pytest)
    }
}
Set-Location $Root
Write-Host "`n=== portfolio_smoke (best-effort) ===" -ForegroundColor Cyan
& "$Root\scripts\portfolio_smoke.ps1"