param(
    [Parameter(Position = 0)]
    [ValidateSet("all", "seed", "index", "eval", "test")]
    [string]$Target = "all"
)
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
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
    "test" { py -3.13 -m pytest -q tests; exit $LASTEXITCODE }
    "all" {
        py -3.13 scripts/init_db.py
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        py -3.13 scripts/seed_synthetic.py
        py -3.13 scripts/seed_golden.py
        py -3.13 scripts/build_index.py
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        py -3.13 scripts/eval_recall.py
        py -3.13 -m pytest -q tests
        exit $LASTEXITCODE
    }
}