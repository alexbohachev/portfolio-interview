[Українська](README.md) | **English**

# Work 7 — AI Platform (Compose MVP+)

**Status:** final run on 2026-11-18, see [`REPORT.en.md`](REPORT.en.md). Ready for tag **`work07-v1.0`** after `.\make.ps1 finalize`.

**In one sentence:** a local stand of **3×Java → FastAPI RAG** with **hybrid search** (work02 corpus, 200 docs) and **Q&A + citations** (extractive or OpenAI).

```powershell
# optional: $env:OPENAI_API_KEY="..."
cd c:\Portfolio\work07-ai-platform
.\make.ps1 all
.\scripts\demo.ps1    # video scenario — DEMO.md
```

| Service | Port |
|---------|------|
| farm / scout / logistics | 8081 / 8082 / 8084 |
| rag-api | 8090 |
| elasticsearch / redpanda / postgres | 9200 / 19092 / 5434 |

## What is implemented (3 steps)

1. **Hybrid + corpus** — mounts `work02-rag-citations/corpus/bundled`, dense kNN + BM25, RRF.
2. **Q&A** — `POST /v1/knowledge/qa` (gate, citations); Java `POST /api/v1/knowledge/qa`.
3. **Demo** — [`DEMO.md`](DEMO.md), [`scripts/demo.ps1`](scripts/demo.ps1).

## Assignment (current slice)

| Requirement | Status |
|-------------|--------|
| Kafka `document.uploaded` / `scout.report.created` | farm + scout → worker → rag-api |
| `recommendation.ready` | worker + `config/actions_catalog.json` |
| Golden **150** (dev 100 + test 50) | `.\make.ps1 seed` → [`DATA.en.md`](DATA.en.md) |
| Recall@5 / MRR | `.\make.ps1 eval` |
| OpenAI (1 provider) | `.\make.ps1 eval-llm` when a key is present |
| Resilience4j | logistics → rag-api |
| OTel | Jaeger UI http://localhost:16687 |
| CI | GitHub Actions + `.gitlab-ci.yml` |

| Recommendation Hit@3 | `.\make.ps1 seed-rec` + `eval-rec` |
| Latency before/after | `X-Search-Profile: slow|fast` + `.\make.ps1 bench` → [`PERFORMANCE.md`](PERFORMANCE.md) |
| OpenAPI rag-api | `.\make.ps1 openapi` |
| DLQ | worker → `document.dlq` |

**Next:** a generated Java client from OpenAPI, k6, tag `work07-v1.0`, a demo video.

[`REPORT.en.md`](REPORT.en.md)
