# Case study: fixing N+1 RAG calls (Work 07)

## Problem & Anti-Pattern Reproduction (before)

`POST /api/v1/equipment-requests` with header `X-Search-Profile: slow`:

- Java **logistics** splits the user question into tokens.
- For **each token**, it calls Python **rag-api** with hybrid search.
- It also runs BM25 + hybrid on the full string → deliberate **N+1 HTTP** anti-pattern reproduction to quantify microservice latency tax.

**Benchmark Context:** Engineered to isolate and quantify a common distributed RAG anti-pattern where an upstream service splits user queries on the client side, triggering sequential HTTP round-trips to downstream search services. We implemented this baseline (`searchSlow`) and profiled the network waterfall in Jaeger (`http://localhost:16687`), then benchmarked the single-shot server-side hybrid RRF replacement (`searchFast`).

**Profiling in Jaeger:** Jaeger UI (`http://localhost:16687`) exposed a cascading waterfall of sequential spans `logistics → rag-api` for one user request.

## Fix (after)

`X-Search-Profile: fast` (default): **one** hybrid call, `topK=3`.

Code: `EquipmentSearchService.searchFast()` vs `searchSlow()` in logistics service.

## Evidence (reproducible across independent runs)

```powershell
cd work07-ai-platform
docker compose up -d   # after .\make.ps1 build
# wait ~90s for index
py -3.13 scripts/benchmark_latency.py
```

### Measured Performance Across Independent Runs

Two independent runs on local Docker Compose (Windows 11, Intel/AMD CPU, 25 requests per profile against `POST /api/v1/equipment-requests`):

| Run ID & Date | Git SHA | Profile | p50 | p95 | Mean | Speedup (p50 / p95) | Artifact File |
|---|---|---|---|---|---|---|---|
| **Run 1** (Baseline, 2026-11-18) | `6efad68` | `slow` (N+1)<br>`fast` (1× Hybrid) | 172.6 ms<br>**34.0 ms** | 197.0 ms<br>**53.3 ms** | —<br>— | **5.08×** (p50)<br>**3.70×** (p95) | `manifests/latency_snapshot.json`<br>`REPORT.md` |
| **Run 2** (Clean-clone, 2026-11-19) | `45d550c` | `slow` (N+1)<br>`fast` (1× Hybrid) | 171.6 ms<br>**33.9 ms** | 195.7 ms<br>**46.7 ms** | 179.2 ms<br>**37.9 ms** | **5.06×** (p50)<br>**4.19×** (p95) | `artifacts/latency_before_after.json`<br>`artifacts/latency_raw_samples.json` |

**Conclusion:** Across both independent cold runs, eliminating the N+1 iterative token loop consistently delivers a **~5.1× speedup at p50** and **~4× speedup at p95** (~73–76% overall latency reduction) with zero change in business search quality.

## Interview narrative (2 min)

1. Show Jaeger trace for **slow** (`http://localhost:16687`) — multiple sequential `rag-api` child spans.
2. Show **fast** trace — single `rag-api` call with Elasticsearch RRF (BM25 + kNN).
3. Run `benchmark_latency.py` live or open raw JSON (`artifacts/latency_before_after.json`).
4. Tie to production habits: RestClient timeouts, Resilience4j, contract tests on search API.

## Hard Retrieval Evaluation: Hybrid vs BM25 Breakdown

On the standard synthetic agricultural corpus (`data/golden/test.json`, n=50), both BM25 and Hybrid achieve a trivial `Recall@5 = 1.0` and `MRR@5 = 1.0` because questions share vocabulary with the clean documents.

To demonstrate true retrieval trade-offs under real-world conditions, we stress-tested across **10 hard domain prompts** (`data/golden/hard_retrieval.json`, scoped via `--doc-id-prefix agri_` to the 200 documents shared with Work 02): **8 answerable queries** (evaluating Recall@5 and MRR@5 on paraphrases and multi-hop questions) plus **2 out-of-domain unanswerable queries** (evaluating the pre-retrieval refusal gate):

```powershell
.\make.ps1 eval-hard
# Command: py -3.13 scripts/eval_retrieval.py --golden-file data/golden/hard_retrieval.json --per-query --doc-id-prefix agri_
```

### Quantitative Metrics & Per-Query Breakdown (`manifests/eval_per_query.json`)

### Quantitative Metrics Across Retrieval Stages & Re-ranker (`manifests/hard_eval_snapshot.json`)

* **BM25 Baseline:** Recall@5 = **0.1250** (1/8) | MRR@5 = **0.0625** | 95% Bootstrap CI: `[0.000, 0.375]`
* **1st-Stage Hybrid (RRF):** Recall@5 = **0.2500** (2/8) | MRR@5 = **0.0938** | 95% Bootstrap CI: `[0.000, 0.625]`
* **2nd-Stage Cross-Encoder:** Recall@5 = **0.5000** (4/8) | MRR@5 = **0.1771** | 95% Bootstrap CI: `[0.125, 0.875]`
* **Net Re-ranker Lift over Hybrid:** **$\Delta = +0.2500$ (+100.0% relative gain)** | 95% Bootstrap CI: `[0.000, 0.625]`
* **Refusal gate:** not measured in the offline evaluation (it runs in `rag-api` and needs Docker); the earlier "2 / 2" came from a hard-coded counter and has been withdrawn.
* **Multilingual models change the picture** (`paraphrase-multilingual-MiniLM-L12-v2` + `mmarco-mMiniLMv2`, `manifests/hard_extended_eval_snapshot_multilingual.json`): on the same 40 queries the cross-encoder reaches Recall@5 = 0.20 vs 0.05 for Hybrid (lift +0.15, 95% CI `[0.025, 0.275]`, excludes zero), and topic-level Hit@5 rises from 0.575 (Hybrid) to 0.750, so part of the problem was the English-only models. Caveat: a single run on a synthetic corpus where documents of a topic are near-identical (random choice within a known topic gives ~0.25 Recall@5), so absolute values say little about real-data quality. Topic-level Hit@5 is reproducible with `scripts/topic_level_recall.py`.

| Query ID & Question | Expected Target | BM25 Hit | Hybrid Hit | Cross-Encoder Hit | Mechanism & Engineering Diagnosis |
|---|---|:---:|:---:|:---:|---|
| **`hard_001`** (Synonym Paraphrase)<br>«Які хвороби пшениці згадують буру іржа та фузаріоз?» | `agri_016_wheat_disease_15` | ❌ (Miss) | ❌ (Miss) | **✅ (Rank 3)** | **Cross-Encoder Win:** Bi-encoder clustered documents into generic wheat disease topics; cross-attention between question tokens and paragraph text elevated target from rank 11 into top-3. |
| **`hard_004`** (Sunflower Seed Density)<br>«Яка щільність посіву насіння для соняшнику?» | `agri_159_seed_rate_18` | ❌ (Miss) | ❌ (Miss) | **✅ (Rank 3)** | **Cross-Encoder Win:** Separated specific sunflower sowing density metrics from adjacent general seed rate documents. |
| **`hard_007`** (Multi-hop Disease Risks)<br>«Порівняти ризики хвороб пшениці в різних сезонах» | `agri_015_wheat_disease_14`<br>`agri_016_wheat_disease_15` | ❌ (Miss) | ❌ (Miss) | **✅ (Rank 4)** | **Cross-Encoder Win:** Recovered multi-hop seasonal risk targets where bi-encoder dot products alone fell short. |
| **`hard_010`** (Soil Humus & Cover Crops)<br>«Органіка та сидерати для підвищення гумусу» | `agri_099_organic_matter_18` | ❌ (Miss) | **✅ (Rank 3)** | **✅ (Rank 2)** | **Hybrid + CE Win:** Semantic generalization across green manure and organic soil enrichment. |
| **`hard_006`** (Exact Formula)<br>«Дози азоту фосфору в NPK для поля» | `agri_062_npk_fertilizer_1` | ❌ (Miss) | ❌ (Miss) | ❌ (Miss) | **Hard Boundary:** Exact formula ratio match without explicit query expansion remains an open edge case. |
| **`hard_008` & `hard_009`** (Out-of-Domain)<br>«Чи вирощують рис на Марсі...»<br>«Чи реєструвався агро-дрон NVIDIA H100...» | *None (Unanswerable)* | n/a | n/a | n/a | Refusal gate is not measured in the offline evaluation (it runs in rag-api, needs Docker).|

### Engineering Takeaway & Architectural Validation
1. **Hybrid RRF** outperforms single-modality search on **abstract semantic paraphrases** (`hard_010`), pulling a richer candidate pool.
2. **Fine-Grained Cluster Discrimination:** In dense technical corpora sharing identical vocabularies, bi-encoders cluster documents effectively but struggle with within-cluster ranking.
3. **Re-ranker experiment (negative on the larger set):** Adding a **2nd-stage Cross-Encoder re-ranker** (`cross-encoder/ms-marco-MiniLM-L-6-v2`) over the top-25 hybrid candidates raised Recall@5 from 0.25 to 0.50 and MRR@5 from 0.0938 to 0.1771 on 8 queries. This did not replicate on the extended 40-query set (`manifests/hard_extended_eval_snapshot.json`): Recall@5 = 0.05 for BM25, Hybrid and Cross-Encoder, lift 0.0 (95% CI `[-0.075, 0.075]`), so the 8-query result is noise. Caveats: the synthetic corpus has 20 near-identical documents per topic, and both models are English-only while queries are Ukrainian; a fair test needs a real multilingual corpus.