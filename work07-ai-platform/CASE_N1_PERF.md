# Case study: fixing N+1 RAG calls (Work 07)

## Problem (before)

`POST /api/v1/equipment-requests` with header `X-Search-Profile: slow`:

- Java **logistics** splits the user question into tokens.
- For **each token**, it calls Python **rag-api** with hybrid search.
- It also runs BM25 + hybrid on the full string → **N+1 HTTP** pattern to rag-api.

**How I found it:** Jaeger UI (`http://localhost:16687`) showed many sequential spans `logistics → rag-api` for one user request.

## Fix (after)

`X-Search-Profile: fast` (default): **one** hybrid call, `topK=3`.

Code: `EquipmentSearchService.searchFast()` vs `searchSlow()` in logistics service.

## Evidence (reproducible)

```powershell
cd work07-ai-platform
docker compose up -d   # after .\make.ps1 build
# wait ~90s for index
py -3.13 scripts/benchmark_latency.py
```

Artifacts:

- `artifacts/latency_before_after.json` — p50/p95 summary
- `artifacts/latency_raw_samples.json` — all 25 samples per profile
- Committed snapshot: `manifests/latency_snapshot.json`

Reference run (local Docker, 2026-11-18):

| Profile | p50 | p95 |
|---------|-----|-----|
| slow | 172.6 ms | 197.0 ms |
| fast | 34.0 ms | 53.3 ms |

**~5.1× p50 speedup**, same functional hits on demo agro queries.

## Interview narrative (2 min)

1. Show Jaeger trace for **slow** — multiple rag-api children.
2. Show **fast** trace — single rag-api call.
3. Run `benchmark_latency.py` live or open raw JSON.
4. Tie to production habits: RestClient timeouts, resilience4j, contract tests on search API.

## Hybrid vs BM25 on harder queries

```powershell
py -3.13 scripts/eval_retrieval.py --golden-file data/golden/hard_retrieval.json --per-query
```

Inspect `artifacts/eval_per_query.json` for queries where hybrid wins, ties, or loses vs BM25 (shared corpus with Work 02).