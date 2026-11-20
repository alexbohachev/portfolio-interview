# Звіт — робота 4 (ML serving)

## Data contract
- `data/DATA_CONTRACT.json`, synthetic `events.parquet`

## Test metrics
> Синтетичні дані з детермінованою міткою: PR-AUC 1.0 / Brier 0.0 означає тривіальну задачу, а не якість моделі.
- Baseline PR-AUC: **0.9456**, Brier **0.0424**
- Candidate PR-AUC: **1.0000**, Brier **0.0000**
- Поріг candidate (val cost): **0.050**

## Serving
- `uvicorn work04.app_main:app` або pytest TestClient

_Час: 7.7 с._
