# Демо work08 для технічного інтерв'ю
$Root = Split-Path -Parent $PSScriptRoot
$env:PYTHONPATH = Join-Path $Root "src"
Set-Location $Root

Write-Host "=== WORK08 DEMO: DEMAND FORECASTING & INVENTORY RISK ===" -ForegroundColor Cyan
Write-Host "1. Офлайн-зведення бектестингу (Seasonal Naive vs LightGBM):" -ForegroundColor Yellow
py -3.13 scripts/demo_offline.py

Write-Host "`n2. Живий онлайн-інференс (/v1/forecast на 14 днів вперед):" -ForegroundColor Yellow
py -3.13 scripts/demo_forecast.py
