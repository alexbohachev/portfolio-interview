[**Українська**](PORTFOLIO.md) | [English](PORTFOLIO.en.md)

# Швидкий індекс проєктів для співбесіди

### 7 основних еталонних проєктів

| № | Проєкт | Опис | Швидка перевірка (Offline) | Живе демо (Live) |
|---|--------|------|---------------------------|-------------------|
| **08** | [`work08-demand-forecasting/`](work08-demand-forecasting/) | Прогнозування попиту, 4-сезонний бектест, Newsvendor ризик, CQR-калібрування | `python scripts/demo_offline.py` | `python scripts/eval_real_benchmark.py` |
| **07** | [`work07-ai-platform/`](work07-ai-platform/) | Відтворення N+1 боттлнеку, Cross-Encoder переранжування, OTel трейси в Jaeger | `python scripts/demo_offline.py` | `docker compose up -d` + `python scripts/benchmark_latency.py` |
| **05** | [`work05-docguard/`](work05-docguard/) | Zero-Trust Pre-LLM ACL шлюз, 8 сценаріїв безпеки + 24 тести ін'єкційних запитів (PromptInjectionIT), degraded fallback | `python scripts/demo_offline.py` | `docker compose up -d` + `bash scripts/reliability_demo.sh` |
| **01** | [`work01-bank-marketing/`](work01-bank-marketing/) | Tabular ML, усунення target leakage (`duration`), часовий сплит, bootstrap CI | `python scripts/demo_offline.py` | `pytest` + `REPORT.md` |
| **04** | [`work04-ml-serving/`](work04-ml-serving/) | Low-latency ML сервінг, data contracts (`event_time`), z-score дрейф | `python scripts/demo_offline.py` | `uvicorn app.main:app` + `/docs` |
| **02** | [`work02-rag-citations/`](work02-rag-citations/) | Гібридний пошук RRF, 2-й етап Cross-Encoder, refusal gate, цитати 35/35 | `python scripts/demo_offline.py` | `pytest` |
| **03** | [`work03-agent-workflow/`](work03-agent-workflow/) | Ідемпотентний оркестратор, Transactional Outbox, 409 Conflict, 30/30 тестів | `python scripts/demo_offline.py` | `docker compose up -d` + `./gradlew bootRun` + `bash scripts/reliability_demo.sh` |

### Допоміжний референс

| № | Проєкт | Опис | Швидка перевірка |
|---|--------|------|-------------------|
| **06** | [`work06-bible-rag/`](work06-bible-rag/) | Автономний семантичний пошук через FAISS + SQLite | `pytest work06-bible-rag/tests` |

---

## Швидка верифікація всього репозиторію

```bash
# Мультиплатформений запуск офлайн-тестів:
python -m pytest work01-bank-marketing/tests work02-rag-citations/tests work04-ml-serving/tests work08-demand-forecasting/tests

# Або через PowerShell smoke runner:
powershell -ExecutionPolicy Bypass -File scripts/portfolio_smoke.ps1
```

## Спільні артефакти та корпус
* **Спільний корпус знань:** `work02-rag-citations/corpus/bundled/` (200 документів `agri_*.md`) — спільна база для Work 02, Work 05 та Work 07.
* **Авторитетні матриці та бенчмарки:** зафіксовані в директоріях `manifests/` кожного проєкту.
