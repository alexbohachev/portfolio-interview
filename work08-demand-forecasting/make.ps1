param(
    [Parameter(Position = 0)]
    [ValidateSet("all", "data", "train", "test", "demo")]
    [string]$Target = "all"
)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$env:PYTHONPATH = Join-Path $Root "src"
Set-Location $Root

if ($Target -eq "data" -or $Target -eq "all") {
    Write-Host "--> Generating dataset..." -ForegroundColor Cyan
    py -3.13 scripts/generate_dataset.py
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

if ($Target -eq "train" -or $Target -eq "all") {
    Write-Host "--> Running backtest and training pipeline..." -ForegroundColor Cyan
    py -3.13 scripts/run_pipeline.py
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

if ($Target -eq "test" -or $Target -eq "all") {
    Write-Host "--> Running tests..." -ForegroundColor Cyan
    py -3.13 -m pytest -v tests
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

if ($Target -eq "demo" -or $Target -eq "all") {
    Write-Host "--> Running demo..." -ForegroundColor Cyan
    py -3.13 scripts/demo_offline.py
    py -3.13 scripts/demo_forecast.py
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

Write-Host "OK work08 finished ($Target)" -ForegroundColor Green
exit 0
