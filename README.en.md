# Portfolio — Senior AI Backend (interview)

Monorepo of **7 production-style projects**: Python ML/RAG, Java microservices, Docker Compose, observability.

**Ukrainian docs:** [`README.md`](README.md) · **Repro:** [`REPRO.md`](REPRO.md) · **Prep:** [`INTERVIEW_PREP.md`](INTERVIEW_PREP.md)

## Three flagship cases

### 1. Work 07 — Distributed RAG platform (show this first)

- **Stack:** Java (farm, scout, logistics) + Python rag-api + Elasticsearch + Kafka + Jaeger.
- **Performance story:** Removed **N+1** calls to rag-api (`X-Search-Profile: slow` vs `fast`) — **p95 ~197 ms → ~53 ms** on local bench.
- **Run:** `cd work07-ai-platform && .\make.ps1 finalize`
- **Read:** [`CASE_N1_PERF.md`](work07-ai-platform/CASE_N1_PERF.md)

### 2. Work 05 — DocGuard (security before the LLM)

- ACL gateway + filtered retrieval; **8/8** security scenarios + Docker smoke.
- **Run:** `cd work05-docguard && docker compose up -d && .\make.ps1 demo`

### 3. Work 02 — RAG with citation gate

- Hybrid RRF vs BM25; refusal threshold on dev (not prompt-only).
- **Run:** `cd work02-rag-citations && .\make.ps1 all && .\make.ps1 demo`

## Quick verify

```powershell
.\scripts\repro_check.ps1
```

## Tags

All seven works: `work01-v1.0` … `work07-v1.0`.

Corpus `work02-rag-citations/corpus/bundled/` (200 docs) is shared with Work 05 and Work 07.