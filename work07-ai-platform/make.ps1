param(
    [Parameter(Position = 0)]
    [ValidateSet("all", "build", "up", "down", "smoke", "jar", "eval", "seed", "eval-llm", "seed-rec", "eval-rec", "bench", "openapi", "finalize", "lock")]
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
    "eval" { py -3.13 scripts/eval_retrieval.py --split test; exit $LASTEXITCODE }
    "seed" { py -3.13 scripts/build_golden_150.py; exit $LASTEXITCODE }
    "eval-llm" { py -3.13 scripts/eval_llm_provider.py; exit $LASTEXITCODE }
    "seed-rec" { py -3.13 scripts/build_recommendation_golden.py; exit $LASTEXITCODE }
    "eval-rec" { py -3.13 scripts/eval_recommendations.py --split test; exit $LASTEXITCODE }
    "bench" { py -3.13 scripts/benchmark_latency.py; exit $LASTEXITCODE }
    "openapi" { py -3.13 scripts/export_openapi.py; exit $LASTEXITCODE }
    "lock" { py -3.13 scripts/lock_manifest.py; exit $LASTEXITCODE }
    "finalize" {
        py -3.13 scripts/smoke_test.py
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        py -3.13 scripts/eval_retrieval.py --split test
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        py -3.13 scripts/eval_recommendations.py --split test
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        py -3.13 scripts/benchmark_latency.py
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        py -3.13 scripts/export_openapi.py
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        py -3.13 scripts/lock_manifest.py
        exit $LASTEXITCODE
    }
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