# Робота 4 — ML-система зі serving

**Одне речення:** табличний **breakdown risk** (синтетика, data contract `event_time` / `available_at`): baseline LR vs **LightGBM + isotonic**, поріг за **FP/FN/review cost**, **FastAPI** `/v1/predict` з версіями моделі.

```powershell
py -3.13 -m pip install -r requirements.txt
.\make.ps1 all
.\make.ps1 test
```

## API

| Endpoint | Опис |
|----------|------|
| `GET /health` | статус + `model_version` |
| `POST /v1/predict` | ймовірність, `decision`, версії |
| `GET /v1/drift` | alert за z-score ознак |

```powershell
$env:PYTHONPATH="src"
py -3.13 -m uvicorn work04.app_main:app --port 8095
```

## Зв'язок з work01

Спільна логіка: temporal split, PR-AUC/Brier, поріг за метою/вартістю.

[`REPORT.md`](REPORT.md) · `data/DATA_CONTRACT.json`