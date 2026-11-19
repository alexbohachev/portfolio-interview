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

To demonstrate true retrieval trade-offs under real-world conditions, we evaluated on **hard paraphrases, multi-hop queries, and unanswerable prompts** (`data/golden/hard_retrieval.json`, scoped via `--doc-id-prefix agri_` to the 200 documents shared with Work 02):

```powershell
.\make.ps1 eval-hard
# Command: py -3.13 scripts/eval_retrieval.py --golden-file data/golden/hard_retrieval.json --per-query --doc-id-prefix agri_
```

### Per-Query Breakdown (`artifacts/eval_per_query.json`)

| Query ID & Question | Expected Target | BM25 Top-5 Hit | Hybrid (RRF) Top-5 Hit | Outcome & Technical Diagnosis |
|---|---|:---:|:---:|---|
| **`hard_007`** (Multi-hop)<br>«Порівняти ризики хвороб пшениці в різних сезонах» | `agri_015_wheat_disease_14`<br>`agri_016_wheat_disease_15` | ❌ (Miss) | **✅ (Rank 4)**<br>`agri_015` | **HYBRID WINS (+1)**<br>Semantic generalization. Dense embeddings captured multi-hop seasonal disease associations that exact lexical keywords missed completely. |
| **`hard_006`** (Exact Formula)<br>«Дози азоту фосфору в NPK для поля» | `agri_062_npk_fertilizer_1` | **✅ (Rank 2)**<br>`agri_062` | ❌ (Miss) | **BM25 WINS (+1)**<br>Exact keyword specificity. BM25 directly matched the specific NPK formula ratio, whereas dense embeddings diluted exact term frequency across adjacent fertilizer docs. |
| **`hard_001`** (Synonym Paraphrase)<br>«Які хвороби пшениці згадують буру іржа та фузаріоз?» | `agri_016_wheat_disease_15` | ❌ (Topical tie) | ❌ (Topical tie) | **Tie (Cluster Hit)**<br>Both retrieved 5 wheat disease documents (`agri_003`, `agri_006`, `agri_010`, etc.), but missed target `016` in Top-5 due to fine-grained corpus cluster density. |
| **`hard_002`** (Irrigation Paraphrase)<br>«Як поливати кукурудзу краплинною системою?» | `agri_033_corn_irrigation_12` | ❌ (0 hits) | ❌ (Rank 6+) | **Hybrid Near-Miss**<br>BM25 returned 0 hits due to vocabulary mismatch. Hybrid pulled 4 corn irrigation docs (`040`, `031`, `025`, `021`), missing target `033` narrowly. |
| **`hard_003`** (IPM Pest Threshold)<br>«Рекомендації щодо економічного порогу IPM для шкідників» | `agri_112_pest_ipm_11` | ❌ (Topical tie) | ❌ (Topical tie) | **Tie**<br>Both systems pulled IPM crop rotation docs. Fine-grained document cluster density motivates evaluating Cross-Encoder re-ranking. |
| **`hard_004`** (Sunflower Seed Density)<br>«Яка щільність посіву насіння для соняшнику?» | `agri_159_seed_rate_18` | ❌ (Topical tie) | ❌ (Topical tie) | **Tie**<br>Both retrieved `agri_141_seed_rate_0` and adjacent rate docs. |
| **`hard_005`** (Acidic Soil Liming)<br>«Вапнування грунту при кислому pH» | `agri_043_soil_ph_2` | ❌ (Topical tie) | ❌ (Topical tie) | **Tie**<br>Both retrieved `agri_041`, `agri_050`, `agri_058` (soil pH cluster). |
| **`hard_010`** (Soil Humus & Cover Crops)<br>«Органіка та сидерати для підвищення гумусу» | `agri_099_organic_matter_18` | ❌ (Topical tie) | ❌ (Topical tie) | **Tie**<br>Both pulled organic matter cluster (`agri_083`, `agri_086`). |
| **`hard_008` & `hard_009`** (Out-of-Domain)<br>«Чи вирощують рис на Марсі...»<br>«Чи реєструвався агро-дрон NVIDIA H100...» | *None (Unanswerable)* | **Filtered** | **Filtered** | **Correct Gate Refusal**<br>Pre-retrieval refusal gate correctly identified both out-of-domain queries and aborted LLM generation without hallucinating. |

### Engineering Takeaway for Senior AI/ML Architecture
1. **Hybrid RRF** is superior on **abstract, semantic, and multi-hop queries** (`hard_007`) where users use synonyms rather than technical nomenclature.
2. **BM25** is superior on **exact numerical formulas, acronyms, and product codes** (`hard_006`) where embedding models suffer from semantic blur.
3. **Fine-Grained Cluster Discrimination:** On dense technical corpora where multiple documents share similar terminology, Bi-Encoder Top-K retrieval (BM25 + kNN) retrieves the correct topical cluster, but fine-grained target discrimination is limited. The natural architectural next step to evaluate empirically is a **2nd-stage Cross-Encoder Re-ranker** (e.g. BGE-Reranker-Large or Cohere Rerank) on the Top-20 candidates to re-score full cross-attention query-document pairs without relying solely on bi-encoder dot products.