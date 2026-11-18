# Звіт — робота 4 (ML serving)

## Data contract
- `data/DATA_CONTRACT.json`, synthetic `events.parquet`

## Test metrics
- Baseline PR-AUC: **0.9456**, Brier **0.0424**
- Candidate PR-AUC: **1.0000**, Brier **0.0000**
- Поріг candidate (val cost): **0.050**

## Serving
- `uvicorn work04.app_main:app` або pytest TestClient

_Час: 7.7 с._
