# Робота 1 — навчання й оцінювання моделей

**Дані:** [UCI Bank Marketing](https://archive.ics.uci.edu/dataset/222/bank+marketing) (`bank-full.csv` з `bank.zip`, CC BY 4.0).  
**Baseline:** логістична регресія (sklearn). **Candidate:** MLP + PyTorch (early stopping).

## Швидкий старт (Windows)

```powershell
py -3.13 -m pip install -r requirements.txt
.\make.ps1 all
```

Очікуваний результат: `artifacts/results.json`, оновлений `REPORT.md`, час — кілька хвилин на CPU.

## Команди

| Команда | Дія |
|---------|-----|
| `.\make.ps1 data` | Завантаження й перевірка SHA-256 |
| `.\make.ps1 all` | Дані → навчання → метрики на test → звіт |
| `.\make.ps1 test` | pytest (split, метрики) |

## Test manifest

Фіксований test: рядки 38430–45211 у файлі (без `duration`). Деталі — `manifests/test_manifest.json`.  
Config hash записується під час першого `all`.

## Git-tag (після приймання роботи)

```bash
git tag -a work01-v1.0 -m "Робота 1: baseline+candidate, REPORT.md"
```

## README для співбесіди (заповнити після фінального test)

1. Одне речення з числом (macro-F1 / PR-AUC).
2. Таблиця baseline vs candidate з інтервалами.
3. Три головні причини помилок.
4. `make all` / `.\make.ps1 all` і час виконання.