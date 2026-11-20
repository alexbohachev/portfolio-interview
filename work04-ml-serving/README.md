[**Українська**](README.md) | [English](README.en.md)

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

## Обмеження

**Обмеження (чесно):** датасет синтетичний, а мітка є детермінованою функцією двох ознак (`maint_score > 0.9` і `hours_used > 8`), тому candidate досягає PR-AUC 1.0 і Brier 0.0: це ознака тривіальної задачі, а не якості моделі. Колонки `feature_available_at` / `label_available_at` лише присутні в даних і JSON-контракті; код навчання та сервінгу їх не використовує (спліт за `event_time`). `/v1/drift` порівнює середні перших 2000 і останніх 500 рядів файлу з випадковим часом, тож є демонстрацією механіки z-score, а не перевіреним моніторингом; тестів на дрейф немає.

## Зв'язок з work01

Спільна логіка: temporal split, PR-AUC/Brier, поріг за метою/вартістю.

[`REPORT.md`](REPORT.md) · `data/DATA_CONTRACT.json`