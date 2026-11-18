param(
    [Parameter(Position = 0)]
    [ValidateSet("all", "build", "up", "down", "smoke", "jar")]
    [string]$Target = "all"
)
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

function Build-Jars {
    & .\gradlew.bat :services:farm:bootJar :services:scout:bootJar :services:logistics:bootJar --no-daemon
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

switch ($Target) {
    "jar" { Build-Jars; exit 0 }
    "build" { Build-Jars; docker compose build; exit $LASTEXITCODE }
    "up" { docker compose up -d; exit $LASTEXITCODE }
    "down" { docker compose down; exit 0 }
    "smoke" { py -3.13 scripts/smoke_test.py; exit $LASTEXITCODE }
    "all" {
        Build-Jars
        docker compose up -d --build
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        Write-Host "Waiting 90s for rag-api (index + embed model)..."
        Start-Sleep -Seconds 90
        py -3.13 scripts/smoke_test.py
        exit $LASTEXITCODE
    }
}