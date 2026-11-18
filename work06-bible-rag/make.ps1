param(
    [Parameter(Position = 0)]
    [ValidateSet("all", "seed", "index", "eval", "test", "lock", "serve", "ui")]
    [string]$Target = "all"
)
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$env:PYTHONPATH = Join-Path $Root "src"
Set-Location $Root

switch ($Target) {
    "seed" {
        py -3.13 scripts/init_db.py
        py -3.13 scripts/seed_synthetic.py
        py -3.13 scripts/seed_golden.py
        exit 0
    }
    "index" { py -3.13 scripts/build_index.py; exit $LASTEXITCODE }
    "eval" { py -3.13 scripts/eval_recall.py; exit $LASTEXITCODE }
    "lock" { py -3.13 scripts/lock.py; exit $LASTEXITCODE }
    "test" { py -3.13 -m pytest -q tests; exit $LASTEXITCODE }
    "serve" {
        py -3.13 -m uvicorn work06.app_main:app --host 127.0.0.1 --port 8098
        exit $LASTEXITCODE
    }
    "ui" {
        py -3.13 -m streamlit run ui/streamlit_app.py
        exit $LASTEXITCODE
    }
    "all" {
        py -3.13 scripts/init_db.py
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        py -3.13 scripts/seed_synthetic.py
        py -3.13 scripts/seed_golden.py
        py -3.13 scripts/build_index.py
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        py -3.13 scripts/eval_recall.py
        py -3.13 scripts/lock.py
        py -3.13 -m pytest -q tests
        exit $LASTEXITCODE
    }
}