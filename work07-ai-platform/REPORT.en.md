[Українська](REPORT.md) | **English**

# Report — Work 7 (AI Platform, Compose MVP)

**Final run date:** 2026-11-18  
**Stand:** local Docker Compose (Windows), work02 corpus of **200** md files.  
**Manifest:** `manifests/test_manifest.json` (`config_hash` = `87dbd806dbe8a914`).

## Architecture

| Layer | Components |
|-------|------------|
| Java | farm, scout, logistics → REST + Kafka |
| Python | rag-api (hybrid, Q&A), worker (index, recommendations, DLQ) |
| Data | Elasticsearch, Redpanda, Postgres, Jaeger (`:16687`) |

## Smoke

`py -3.13 scripts/smoke_test.py` — **OK** (indexed=200, hybrid, Q&A via logistics, Kafka farm/scout, slow profile).

## Retrieval (golden test, n=50)

| Metric | BM25 | Hybrid |
|--------|------|--------|
| Recall@5 | **1.00** | **1.00** |
| MRR@5 | **1.00** | **1.00** |

Source: `data/golden/test.json` (50 new work07 questions). Artifact: `artifacts/eval_results.json`.

## Recommendations (test, n=20)

| Metric | Value |
|--------|-------|
| Hit@3 | **0.65** |
| precision@3 | **0.23** |
| citation_support_rate | **0.23** |

Heuristic matcher + a catalogue of 30 actions; improvement path — an ML/LLM candidate. Artifact: `artifacts/recommendation_eval.json`.

## logistics → rag-api performance

`scripts/benchmark_latency.py` (n=25 per profile, `POST /api/v1/equipment-requests`):

| Run | Date and Git SHA | Conditions | slow profile (N+1) | fast profile (1× Hybrid) | Speedup (p50 / p95) | Artifacts |
|---|---|---|---|---|---|---|
| **Run 1** (Baseline) | 2026-11-18 (`6efad68`) | Local Docker Compose, Win11 | p50: **172.6 ms**<br>p95: **197.0 ms** | p50: **34.0 ms**<br>p95: **53.3 ms** | **5.08×** (p50)<br>**3.70×** (p95) | `manifests/latency_snapshot.json` |
| **Run 2** (Clean-clone) | 2026-11-19 (`45d550c`) | Full container restart, Win11 | p50: **171.6 ms**<br>p95: **231.5 ms** | p50: **33.9 ms**<br>p95: **46.9 ms** | **5.06×** (p50)<br>**4.94×** (p95) | `manifests/latency_before_after.json`<br>`manifests/latency_raw_samples.json` |

Both independent runs confirm a stable latency reduction of **~5.1× at p50** and **~4–5× at p95** (Run 1: 3.70× with the old method; Run 2: 4.94×; ~80% latency reduction in Run 2) with no degradation of search results. Detailed analysis: [`CASE_N1_PERF.md`](CASE_N1_PERF.md). Method note: Run 2 percentiles are recomputed with linear interpolation (numpy default) from the committed raw samples (`manifests/latency_raw_samples.json`). The first p95 figures (195.7 / 46.7 ms) were computed with a floor index (the 23rd of 25 values, about p92) and are superseded. With n=25 the p95 rests on the two slowest requests, so it is indicative; Run 1 is kept as originally recorded (old method, no raw samples).

## Retrieval on hard queries (`eval-hard`, n=8 evaluated)

`.\make.ps1 eval-hard` (or `py -3.13 scripts/eval_retrieval.py --golden-file data/golden/hard_retrieval.json --per-query --doc-id-prefix agri_`):

| Query | Target doc_id | BM25 Hit@5 | Hybrid Hit@5 | Comparison summary |
|---|---|:---:|:---:|---|
| `hard_007`: «Порівняти ризики хвороб пшениці в різних сезонах» | `agri_015_wheat_disease_14` | ❌ (Miss) | **✅ (Rank 4)** | **Hybrid won (+1)**: semantic generalization linking diseases and seasons |
| `hard_006`: «Дози азоту фосфору в NPK для поля» | `agri_062_npk_fertilizer_1` | **✅ (Rank 2)** | ❌ (Miss) | **BM25 won (+1)**: exact match of terms and formula proportions |
| `hard_001`–`005`, `010`: paraphrases and synonyms | Various (agro clusters) | ❌ | ❌ | **Cluster parity**: relevant clusters were found; the hypothesis for the test is a cross-encoder |
| `hard_008`, `hard_009`: irrelevant (out of domain) | None | Filtered | Filtered | **Correct refusal (Gate)**: zero hallucinations |

Artifacts: `manifests/hard_eval_snapshot.json` and `artifacts/eval_per_query.json`.

## Other (MVP)

- Resilience4j on logistics; read timeout 120s.
- OpenAPI: `openapi/rag-api.openapi.json`.
- OTel: Java + FastAPI → Jaeger **http://localhost:16687**.
- OpenAI: `.\make.ps1 eval-llm` is optional (the key is not in the repository).

## Limitations (honestly)

- Recall 1.0 is on the **synthetic** work02 corpus (expected to be inflated vs open data).
- Recommendations: rule-based, not the Hit@3 against the assignment's reference of 40 labeled observations in production.
- A generated Java OpenAPI client, k6 and a second embeddings index come after the MVP.

## Acceptance (work07-v1.0)

```powershell
cd c:\Portfolio\work07-ai-platform
.\make.ps1 all          # or up + smoke after the jar
.\make.ps1 finalize    # smoke + eval + bench + lock
```

After the commit: `git tag -a work07-v1.0 -m "Робота 7: Compose AI platform MVP"`.

## Demo

* 🎬 **Demo video (MP4 walkthrough):** [`assets/work07_demo_walkthrough.mp4`](../assets/work07_demo_walkthrough.mp4) — a video presentation of the architecture, Jaeger traces and measured p50/p95 timings.
* **Step-by-step script:** [`DEMO_SCRIPT_5MIN.en.md`](DEMO_SCRIPT_5MIN.en.md), `DEMO.md`, `scripts/demo.ps1`.
* **Live run in the terminal:** `.\scripts\live_interview.ps1 work07`.
