param(
    [Parameter(Position = 0)]
    [ValidateSet("all", "test")]
    [string]$Target = "all"
)
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root
if ($Target -eq "test") { & .\gradlew.bat test --no-daemon; exit $LASTEXITCODE }
& .\gradlew.bat test --no-daemon
exit $LASTEXITCODE