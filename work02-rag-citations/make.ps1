param(
    [Parameter(Position = 0)]
    [ValidateSet("all", "seed", "test", "lock", "eval-llm")]
    [string]$Target = "all"
)
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$env:PYTHONPATH = Join-Path $Root "src"
Set-Location $Root
if ($Target -eq "eval-llm") { py -3.13 -m work02 eval-llm; exit $LASTEXITCODE }
py -3.13 -m work02 $Target
exit $LASTEXITCODE