# Демо work04 (2–4 хв)

```powershell
cd c:\Portfolio\work04-ml-serving
py -3.13 -m pip install -r requirements.txt
.\make.ps1 all
.\scripts\demo.ps1
```

Опційно сервер:

```powershell
$env:PYTHONPATH="src"
py -3.13 -m uvicorn work04.app_main:app --port 8095
```

## Сценарій

1. `scripts/demo_offline.py` — health + predict (TestClient).
2. Пояснити **data contract** `event_time` / `available_at`.
3. **LR vs LightGBM+isotonic**, поріг за cost, `GET /v1/drift`.
4. Rollback тест у `make.ps1 test`.