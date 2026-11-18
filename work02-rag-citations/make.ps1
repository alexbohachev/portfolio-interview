param(
    [Parameter(Position = 0)]
    [ValidateSet("all", "seed", "test")]
    [string]$Target = "all"
)
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$env:PYTHONPATH = Join-Path $Root "src"
Set-Location $Root
py -3.13 -m work02 $Target
exit $LASTEXITCODE