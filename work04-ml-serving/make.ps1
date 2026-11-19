param(
    [Parameter(Position = 0)]
    [ValidateSet("all", "seed", "test", "lock", "demo")]
    [string]$Target = "all"
)
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$env:PYTHONPATH = Join-Path $Root "src"
Set-Location $Root
if ($Target -eq "all") {
    py -3.13 scripts/seed_data.py
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
if ($Target -eq "lock") { py -3.13 -m work04 lock; exit $LASTEXITCODE }
if ($Target -eq "demo") { & "$Root\scripts\demo.ps1"; exit $LASTEXITCODE }
py -3.13 -m work04 $Target
exit $LASTEXITCODE