[Українська](DEMO.md) | **English**

# Demo work04 (2–4 min)

```powershell
cd c:\Portfolio\work04-ml-serving
py -3.13 -m pip install -r requirements.txt
.\make.ps1 all
.\scripts\demo.ps1
```

Optional server:

```powershell
$env:PYTHONPATH="src"
py -3.13 -m uvicorn work04.app_main:app --port 8095
```

## Script

1. `scripts/demo_offline.py` — health + predict (TestClient).
2. Explain the `event_time` / `available_at` data contract (declared in the data; not yet enforced by code).
3. **LR vs LightGBM+isotonic**, threshold by cost, `GET /v1/drift`.
4. Rollback test in `make.ps1 test`.
