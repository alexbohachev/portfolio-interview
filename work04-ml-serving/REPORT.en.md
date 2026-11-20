[Українська](REPORT.md) | **English**

# Report — work 4 (ML serving)

## Data contract
- `data/DATA_CONTRACT.json`, synthetic `events.parquet`

## Test metrics
> Synthetic data with a deterministic label: PR-AUC 1.0 / Brier 0.0 means a trivial task, not model quality.
- Baseline PR-AUC: **0.9456**, Brier **0.0424**
- Candidate PR-AUC: **1.0000**, Brier **0.0000**
- Candidate threshold (val cost): **0.050**

## Serving
- `uvicorn work04.app_main:app` or pytest TestClient

_Time: 7.7 s._
