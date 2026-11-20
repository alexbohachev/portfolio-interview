[Українська](README.md) | **English**

# Work 4 — ML System with Serving

**In one sentence:** tabular **breakdown risk** (synthetic data, data contract `event_time` / `available_at`): baseline LR vs **LightGBM + isotonic**, threshold by **FP/FN/review cost**, **FastAPI** `/v1/predict` with model versions.

```powershell
py -3.13 -m pip install -r requirements.txt
.\make.ps1 all
.\make.ps1 test
```

## API

| Endpoint | Description |
|----------|-------------|
| `GET /health` | status + `model_version` |
| `POST /v1/predict` | probability, `decision`, versions |
| `GET /v1/drift` | alert based on feature z-score |

```powershell
$env:PYTHONPATH="src"
py -3.13 -m uvicorn work04.app_main:app --port 8095
```

## Limitations

**Limitations (honestly):** the dataset is synthetic and the label is a deterministic function of two features (`maint_score > 0.9` and `hours_used > 8`), so the candidate reaches PR-AUC 1.0 and Brier 0.0: this signals a trivial task, not model quality. The `feature_available_at` / `label_available_at` columns are only present in the data and in the JSON contract; the training and serving code does not use them (the split is by `event_time`). `/v1/drift` compares the means of the first 2000 and last 500 rows of a file with random timestamps, so it demonstrates the z-score mechanics rather than being verified monitoring; there are no drift tests.

## Relation to work01

Shared logic: temporal split, PR-AUC/Brier, threshold by objective/cost.

[`REPORT.md`](REPORT.md) · `data/DATA_CONTRACT.json`
