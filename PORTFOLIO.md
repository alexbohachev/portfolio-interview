# Швидкий довідник для співбесіди

| № | Робота | Тег | Одна команда | Головна ідея |
|---|--------|-----|--------------|--------------|
| 1 | work01-bank-marketing | work01-v1.0 | `.\make.ps1 all` | ML pipeline, leakage guard |
| 2 | work02-rag-citations | work02-v1.0 | `.\make.ps1 all` | BM25 vs hybrid RRF + refusal gate |
| 3 | work03-agent-workflow | work03-v1.0 | `.\make.ps1 all` | Orchestrator + outbox + fault matrix |
| 7 | work07-ai-platform | work07-v1.0 | `.\make.ps1 finalize` | Java↔Python RAG, Kafka, ES, Jaeger |
| 4 | work04-ml-serving | work04-v1.0 | `.\make.ps1 all` | Serving, drift, rollback |
| 5 | work05-docguard | work05-v1.0 | `.\make.ps1 all` | ACL gateway + filtered retrieval |
| 6 | work06-bible-rag | work06-v1.0 | `.\make.ps1 all` | E5+FAISS, API :8098, Streamlit |

## Демо (рекомендований порядок на екрані)

1. **work07** — повна платформа ([`work07-ai-platform/DEMO.md`](work07-ai-platform/DEMO.md))
2. **work05** — `docker compose up` + `.\make.ps1 smoke` (ACL до retrieval)
3. **work02** — `.\make.ps1 demo` (метрики + gate)
4. **work06** — `.\make.ps1 serve` + `.\make.ps1 demo` або UI

```powershell
.\scripts\portfolio_smoke.ps1
```

## Спільний корпус

`work02-rag-citations/corpus/bundled/` (200 × `agri_*.md`) — використовується в work05, work07.