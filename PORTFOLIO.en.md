[Українська](PORTFOLIO.md) | **English**

# Quick project index for the interview

### 7 main reference projects

| # | Project | Description | Quick check (Offline) | Live demo (Live) |
|---|--------|------|---------------------------|-------------------|
| **08** | [`work08-demand-forecasting/`](work08-demand-forecasting/) | Demand forecasting, 4-season backtest, Newsvendor risk, CQR calibration | `python scripts/demo_offline.py` | `python scripts/eval_real_benchmark.py` |
| **07** | [`work07-ai-platform/`](work07-ai-platform/) | Reproduction of the N+1 bottleneck, Cross-Encoder reranking, OTel traces in Jaeger | `python scripts/demo_offline.py` | `docker compose up -d` + `python scripts/benchmark_latency.py` |
| **05** | [`work05-docguard/`](work05-docguard/) | Zero-Trust Pre-LLM ACL gateway, 8 security scenarios + 24 injection-style query tests (PromptInjectionIT), degraded fallback | `python scripts/demo_offline.py` | `docker compose up -d` + `bash scripts/reliability_demo.sh` |
| **01** | [`work01-bank-marketing/`](work01-bank-marketing/) | Tabular ML, elimination of target leakage (`duration`), time-based split, bootstrap CI | `python scripts/demo_offline.py` | `pytest` + `REPORT.md` |
| **04** | [`work04-ml-serving/`](work04-ml-serving/) | Low-latency ML serving, data contracts (`event_time`), z-score drift | `python scripts/demo_offline.py` | `uvicorn app.main:app` + `/docs` |
| **02** | [`work02-rag-citations/`](work02-rag-citations/) | Hybrid RRF search, 2nd-stage Cross-Encoder, refusal gate, citations 35/35 | `python scripts/demo_offline.py` | `pytest` |
| **03** | [`work03-agent-workflow/`](work03-agent-workflow/) | Idempotent orchestrator, Transactional Outbox, 409 Conflict, 30/30 tests | `python scripts/demo_offline.py` | `docker compose up -d` + `./gradlew bootRun` + `bash scripts/reliability_demo.sh` |

### Supporting reference

| # | Project | Description | Quick check |
|---|--------|------|-------------------|
| **06** | [`work06-bible-rag/`](work06-bible-rag/) | Standalone semantic search via FAISS + SQLite | `pytest work06-bible-rag/tests` |

---

## Quick verification of the whole repository

```bash
# Cross-platform run of the offline tests:
python -m pytest work01-bank-marketing/tests work02-rag-citations/tests work04-ml-serving/tests work08-demand-forecasting/tests

# Or via the PowerShell smoke runner:
powershell -ExecutionPolicy Bypass -File scripts/portfolio_smoke.ps1
```

## Shared artifacts and corpus
* **Shared knowledge corpus:** `work02-rag-citations/corpus/bundled/` (200 `agri_*.md` documents) — the common base for Work 02, Work 05 and Work 07.
* **Authoritative matrices and benchmarks:** recorded in the `manifests/` directories of each project.
