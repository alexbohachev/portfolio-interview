# Робота 7 — AI-платформа (Compose MVP+)

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

## MVP vs ТЗ (далі)

- Golden 150, Recall@5, один **оцінений** LLM-провайдер
- Kafka події scout → worker (розширити)
- GitLab CI, OTel, Resilience4j

[`REPORT.md`](REPORT.md)