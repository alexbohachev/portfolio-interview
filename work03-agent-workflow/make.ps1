param(
    [Parameter(Position = 0)]
    [ValidateSet("all", "test", "boot", "demo")]
    [string]$Target = "all"
)
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root
if ($Target -eq "all" -or $Target -eq "test") {
    & .\gradlew.bat test
    exit $LASTEXITCODE
}
if ($Target -eq "boot") {
    & .\gradlew.bat bootRun
    exit $LASTEXITCODE
}
if ($Target -eq "demo") {
    & "$Root\scripts\demo.ps1"
    exit $LASTEXITCODE
}