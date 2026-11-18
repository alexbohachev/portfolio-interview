param(
    [Parameter(Position = 0)]
    [ValidateSet("all", "seed", "test", "lock", "eval-llm", "demo", "verify-sources")]
    [string]$Target = "all"
)
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$env:PYTHONPATH = Join-Path $Root "src"
Set-Location $Root
if ($Target -eq "eval-llm") { py -3.13 -m work02 eval-llm; exit $LASTEXITCODE }
if ($Target -eq "demo") { & "$Root\scripts\demo.ps1"; exit $LASTEXITCODE }
if ($Target -eq "verify-sources") { py -3.13 scripts/verify_sources.py; exit $LASTEXITCODE }
py -3.13 -m work02 $Target
exit $LASTEXITCODE