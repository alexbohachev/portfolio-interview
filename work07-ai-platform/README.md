# Робота 7 — AI-платформа (Compose MVP+)

**Статус:** фінальний прогон 2026-11-18 — див. [`REPORT.md`](REPORT.md). Готово до tag **`work07-v1.0`** після `.\make.ps1 finalize`.

**Одне речення:** локальний стенд **3×Java → FastAPI RAG** з **hybrid search** (корпус work02, 200 docs), **Q&A + citations** (extractive або OpenAI).

```powershell
# опційно: $env:OPENAI_API_KEY="..."
cd c:\Portfolio\work07-ai-platform
.\make.ps1 all
.\scripts\demo.ps1    # сценарій для відео — DEMO.md
```

| Сервіс | Порт |
|--------|------|
| farm / scout / logistics | 8081 / 8082 / 8084 |
| rag-api | 8090 |
| elasticsearch / redpanda / postgres | 9200 / 19092 / 5434 |

## Що реалізовано (3 кроки)

1. **Hybrid + корпус** — mount `work02-rag-citations/corpus/bundled`, dense+kNN + BM25, RRF.
2. **Q&A** — `POST /v1/knowledge/qa` (gate, citations); Java `POST /api/v1/knowledge/qa`.
3. **Демо** — [`DEMO.md`](DEMO.md), [`scripts/demo.ps1`](scripts/demo.ps1).

## ТЗ (поточний зріз)

| Вимога | Статус |
|--------|--------|
| Kafka `document.uploaded` / `scout.report.created` | farm + scout → worker → rag-api |
| `recommendation.ready` | worker + `config/actions_catalog.json` |
| Golden **150** (dev 100 + test 50) | `.\make.ps1 seed` → [`DATA.md`](DATA.md) |
| Recall@5 / MRR | `.\make.ps1 eval` |
| OpenAI (1 провайдер) | `.\make.ps1 eval-llm` за наявності ключа |
| Resilience4j | logistics → rag-api |
| OTel | Jaeger UI http://localhost:16687 |
| CI | GitHub Actions + `.gitlab-ci.yml` |

| Hit@3 рекомендації | `.\make.ps1 seed-rec` + `eval-rec` |
| Latency до/після | `X-Search-Profile: slow|fast` + `.\make.ps1 bench` → [`PERFORMANCE.md`](PERFORMANCE.md) |
| OpenAPI rag-api | `.\make.ps1 openapi` |
| DLQ | worker → `document.dlq` |

**Далі:** згенерований Java-клієнт з OpenAPI, k6, tag `work07-v1.0`, демо-відео.

[`REPORT.md`](REPORT.md)