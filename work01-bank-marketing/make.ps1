param(
    [Parameter(Position = 0)]
    [ValidateSet("all", "data", "test", "lock", "demo")]
    [string]$Target = "all"
)

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$env:PYTHONPATH = Join-Path $Root "src"
Set-Location $Root
# Python 3.12+ (на цій машині — 3.13; 3.14 ще без wheels для частини пакетів)
if ($Target -eq "demo") { & "$Root\scripts\demo.ps1"; exit $LASTEXITCODE }
py -3.13 -m work01 $Target
exit $LASTEXITCODE