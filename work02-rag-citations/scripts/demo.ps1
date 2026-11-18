$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root
$env:PYTHONPATH = Join-Path $Root "src"
py -3.13 scripts/demo_offline.py
exit $LASTEXITCODE