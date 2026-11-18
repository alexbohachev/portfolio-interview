param(
    [Parameter(Position = 0)]
    [ValidateSet("all", "test", "compose-up", "compose-down", "smoke", "load")]
    [string]$Target = "all"
)
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

switch ($Target) {
    "test" {
        & .\gradlew.bat test --no-daemon
        exit $LASTEXITCODE
    }
    "compose-up" {
        docker compose up -d --build
        exit $LASTEXITCODE
    }
    "compose-down" {
        docker compose down
        exit 0
    }
    "smoke" {
        & "$Root\scripts\smoke.ps1"
        exit $LASTEXITCODE
    }
    "load" {
        py -3.13 "$Root\scripts\load_probe.py" --duration-sec 60 --rps 1
        exit $LASTEXITCODE
    }
    "all" {
        & .\gradlew.bat test --no-daemon
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        if (Get-Command docker -ErrorAction SilentlyContinue) {
            docker compose up -d --build
            if ($LASTEXITCODE -eq 0) {
                & "$Root\scripts\smoke.ps1"
                exit $LASTEXITCODE
            }
        }
        Write-Host "SKIP compose/smoke (docker unavailable)"
        exit 0
    }
}