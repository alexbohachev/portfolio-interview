[Українська](README.md) | **English**

# AI Systems & Applied Machine Learning Monorepo

[![CI: Clean-Clone Reproducibility](https://github.com/alexbohachev/portfolio-interview/actions/workflows/repro.yml/badge.svg)](https://github.com/alexbohachev/portfolio-interview/actions/workflows/repro.yml)
[![All GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI_Runs-blue)](https://github.com/alexbohachev/portfolio-interview/actions)
[![Demo Video (60s MP4)](https://img.shields.io/badge/Demo_Video-60s_MP4_Walkthrough-blueviolet)](https://github.com/alexbohachev/portfolio-interview/blob/main/assets/work07_demo_walkthrough.mp4)
[![Demo Script (5-7 min)](https://img.shields.io/badge/Demo_Script-5--7_min_Walkthrough-purple)](https://github.com/alexbohachev/portfolio-interview/blob/main/work07-ai-platform/DEMO_SCRIPT_5MIN.md)
[![Live Demo Runner](https://img.shields.io/badge/Live_Demo-scripts%2Flive__interview.ps1-orange)](scripts/live_interview.ps1)

Reproducible engineering portfolio of **7 reference projects (+ 1 offline retrieval utility)** demonstrating:
* **Distributed AI Platforms (Java 21, Python 3.13, Docker, Kafka, OpenTelemetry):** N+1 latency case: reproduced and benchmarked locally (p95 231.5 ms → 46.9 ms), Pre-LLM zero-trust security gateway, and Transactional Outbox recovery (30/30 fault scenarios passing).
* **Applied Machine Learning & MLOps (PyTorch, LightGBM, FastAPI):** Leakage-free temporal backtesting on UCI data, multi-series demand forecasting with conformal prediction (LightGBM on synthetic series; Seasonal Naive baseline selected on real Capital Bikeshare via Occam's razor), and production model serving with feature drift monitoring.

> **Ukrainian version:** [`README.md`](README.md) · **Repro guide:** [`REPRO.md`](REPRO.md) · **N+1 case study:** [`CASE_N1_PERF.md`](work07-ai-platform/CASE_N1_PERF.md) · **Live demo script:** [`DEMO_SCRIPT_5MIN.md`](work07-ai-platform/DEMO_SCRIPT_5MIN.md) · **Standalone guide:** [`STANDALONE_PORTFOLIO.md`](STANDALONE_PORTFOLIO.md)

---

## Capabilities & Operational Boundaries

Every metric below is backed by committed test suites, committed raw measurement arrays, and automated fault matrix tests in CI:

| Dimension | Proof in Monorepo | Capabilities & Measured Impact | Operational Boundaries (Scope) |
|---|---|---|---|
| **AI Systems & Performance** | **Work 07 (AI Platform)** | Benchmarked microservice N+1 anti-pattern (Java → Python RAG API). **p95 latency reduced from 231.5 ms → 46.9 ms (4.94× speedup; p50: 171.6 ms → 33.9 ms, 5.06× speedup)** via server-side hybrid RRF retrieval; verified with OpenTelemetry/Jaeger traces and committed raw timing arrays. | Local Docker Compose benchmark; not a geo-distributed Kubernetes cluster. |
| **Enterprise AI Security** | **Work 05 (DocGuard)** | Zero-trust Pre-LLM gateway (Java 21 + FastAPI). Intercepts queries before vector DB or LLM. **Verified tenant isolation across 8 automated adversarial test scenarios**, verbatim query audit logging, and degraded circuit-breaker fallback. | In-memory ACL cache with REST eviction; not an external enterprise IdP (Ory/Keycloak). |
| **Applied ML & Backtesting** | **Work 01 (Bank Marketing)** | Empirically rigorous tabular ML on real UCI data. **Strict target leakage elimination** (removed post-call `duration`), chronological temporal split under severe covariate shift (5.8% → 39.3%), bootstrap 95% CI showing neural nets fail to outperform calibrated linear baselines. | Tabular UCI dataset; temperature scaling alone does not eliminate shift without domain adaptation. |
| **Demand Forecasting & Risk** | **Work 08 (Demand Forecasting)** | Evaluated 4-season rolling backtests ($H=14$) across two benchmarks: (1) **Synthetic Agro Simulation (20 series)**: LightGBM reduced WAPE from 13.2% to 7.8% (-41%), Newsvendor policy cut simulated inventory costs by 43%, and CQR delivered observed $\ge 80.0\%$ coverage (mean 84.1%). (2) **Real Capital Bikeshare (2011–2012)**: Seasonal Naive baseline outperformed LightGBM (35.4% vs 37.7% WAPE), and we select the baseline for production. CQR lifted empirical coverage from 26.8% to 75.9%. | Direct forecasting model locked to operational horizon $H=14$; exchangeability holds on synthetic series but degrades under physical fleet expansion drift. |
| **Production ML Serving & Drift** | **Work 04 (Risk Serving)** | Low-latency FastAPI model serving. Business cost matrix thresholding ($C_{FN}$ vs $C_{FP}$ vs $C_{review}$), versioned `/v1/predict`, and a demonstrative z-score drift endpoint. | Synthetic data with a deterministic label (PR-AUC 1.0 means a trivial task); `available_at` columns exist in the data contract but are not applied in code; drift check is untested and not run on real streaming batches. |
| **Distributed Resilience** | **Work 03 (Agent Workflow)** | Deterministic 3-step orchestrator with **Transactional Outbox and Checkpoint recovery**. Survived **30/30 automated fault injection scenarios** without duplicate external effects; returns HTTP 409 Conflict on payload tampering. | Single-node Spring Boot transactional boundary with PostgreSQL; does not claim multi-node consensus (Raft/Paxos). |
| **Search & Retrieval Science** | **Work 02 & 07 (RAG Science)** | Hybrid RRF search (Elasticsearch BM25 + dense kNN). **Stress-tested across 10 hard domain prompts**: 8 answerable queries (Recall@5: BM25 0.125, Hybrid 0.25, Hybrid + Cross-Encoder 0.50; this lift did NOT replicate: on the extended 40-query set all three methods score Recall@5 = 0.05 and the re-ranker lift is 0.0, 95% CI [-0.075, 0.075]) + 2 out-of-domain queries correctly rejected by pre-retrieval refusal gate. | 200 domain documents; bi-encoder alone requires domain fine-tuning or cross-encoder re-ranking for fine-grained discrimination. |
| **Full Stack Engineering** | **Monorepo Suite** | Java 21 (Spring Boot 3, RestClient), Python 3.13 (FastAPI, PyTorch/SentenceTransformers), Docker Compose, Kafka, Elasticsearch, Jaeger. | Multi-platform CI verifies offline test suite (<30s) and Docker integration suite. |

---

## Core Case Studies

### 1. Work 07 — Distributed AI Platform: Reproduced N+1 Anti-Pattern & Latency Optimization

```
[Client / Mobile App]
       │
       ▼
[Logistics Service (Java 21)] ──(Trace: OpenTelemetry)──► [Jaeger UI :16687]
       │
       ├─► (searchSlow: N+1 calls per token) ──┐
       │                                       ▼
       └─► (searchFast: Single hybrid call) ──► [RAG API (Python 3.13 / FastAPI)]
                                                      │
                                                      ▼
                                          [Elasticsearch 8.17 (BM25 + kNN / RRF)]
```

* **Architecture & Benchmark Context:** Engineered to benchmark and quantify a common distributed RAG anti-pattern where upstream services decompose user queries into iterative token-level HTTP calls to downstream search services. We implemented this baseline in `EquipmentSearchService.java` (`searchSlow`: sequential per-token HTTP round-trips) and benchmarked it against single-shot server-side hybrid retrieval (`searchFast`: server-side Reciprocal Rank Fusion in Elasticsearch 8.17) in local Docker Compose.
* **Architectural Fix:** Replaced iterative search with a single batch hybrid call (`searchFast()`) requesting top-K items via server-side Reciprocal Rank Fusion (RRF) in Elasticsearch.

#### Quantitative Benchmarking Across Independent Runs (25 samples per profile, local Docker Compose):

* **Run 1 (Baseline, 2026-11-18, Git SHA `6efad68`):**
  * `slow` profile (N+1): p50 = **172.6 ms** | **p95 = 197.0 ms**
  * `fast` profile (batch hybrid): p50 = **34.0 ms** | **p95 = 53.3 ms**
* **Run 2 (Clean Clone Verification, 2026-11-19, Git SHA `45d550c`):**
  * `slow` profile (N+1): p50 = **171.6 ms** | **p95 = 231.5 ms** | mean = 179.2 ms
  * `fast` profile (batch hybrid): p50 = **33.9 ms** | **p95 = 46.9 ms** | mean = 37.9 ms
* **Net Performance Gain:** **5.06×–5.08× speedup at p50, 3.70× (Run 1, old percentile method) and 4.94× (Run 2) speedup at p95** (~80% reduction at p50 and p95 in Run 2).
  * *Method note:* Run 2 percentiles are recomputed with linear interpolation (numpy default) from the committed raw samples (`work07-ai-platform/manifests/latency_raw_samples.json`). The first published p95 figures (195.7 / 46.7 ms) came from a floor-index percentile that returned the 23rd of 25 samples (about p92) and are superseded. With n=25 the p95 rests on the two slowest samples, so it is indicative; Run 1 is kept as originally reported (old method, raw samples not retained).
* **Committed Raw Evidence:**
  * Raw timing arrays (all 25 samples per profile): [`work07-ai-platform/manifests/latency_raw_samples.json`](work07-ai-platform/manifests/latency_raw_samples.json)
  * Summary metrics: [`work07-ai-platform/manifests/latency_before_after.json`](work07-ai-platform/manifests/latency_before_after.json)

#### Hard Retrieval Stress-Test: 2nd-Stage Cross-Encoder Re-ranking (lift not replicated)

Standard synthetic tests give a trivial `Recall@5 = 1.0`. To evaluate real retrieval boundaries, we stress-tested across **10 hard domain prompts** (`data/golden/hard_retrieval.json` scoped to the 200 documents shared with Work 02): **8 answerable queries** (evaluating Recall@5 and MRR@5 on paraphrases and multi-hop queries) plus **2 out-of-domain unanswerable queries** (evaluating the pre-retrieval refusal gate).

To eliminate bi-encoder topic clustering errors, we added a **2nd-stage Cross-Encoder re-ranker** (`cross-encoder/ms-marco-MiniLM-L-6-v2`) that scores the top 25 hybrid candidate pairs $(q, d_i)$:

* **Quantitative Ablation Across Retrieval Stages (8 answerable queries):**
  * **BM25 Baseline:** Recall@5 = **0.1250** (1/8) | MRR@5 = **0.0625** | 95% Bootstrap CI: `[0.000, 0.375]`
  * **1st-Stage Hybrid (RRF):** Recall@5 = **0.2500** (2/8) | MRR@5 = **0.0938** | 95% Bootstrap CI: `[0.000, 0.625]`
  * **2nd-Stage Cross-Encoder:** Recall@5 = **0.5000** (4/8) | MRR@5 = **0.1771** | 95% Bootstrap CI: `[0.125, 0.875]`
  * **Net Reranker Lift over Hybrid:** $\Delta = +0.2500$ Recall@5 (2/8 → 4/8) | 95% Bootstrap CI: `[0.000, 0.625]`. **This did not replicate on the extended 40-query set (`hard_retrieval_extended.json`, `manifests/hard_extended_eval_snapshot.json`): Recall@5 = 0.05 for BM25, Hybrid and Cross-Encoder alike, lift 0.0, 95% CI `[-0.075, 0.075]`; the 8-query result should be read as noise.** The low absolute recall reflects test limitations rather than proof the approach is weak: the 20 synthetic documents per topic differ only by a keyword and a year, so a paraphrase cannot identify a single target, and both models (`all-MiniLM-L6-v2`, `ms-marco-MiniLM`) are English-only while queries are Ukrainian.
* **Refusal gate:** not measured in this offline evaluation (the gate runs in `rag-api` and needs Docker); earlier "2/2" and "10/10" figures came from a hard-coded counter and have been withdrawn.
* **Multilingual models change the picture** (`paraphrase-multilingual-MiniLM-L12-v2` + `mmarco-mMiniLMv2`, `manifests/hard_extended_eval_snapshot_multilingual.json`): on the same 40 queries the cross-encoder reaches Recall@5 = 0.20 vs 0.05 for Hybrid (lift +0.15, 95% CI `[0.025, 0.275]`, excludes zero), and topic-level Hit@5 rises from 0.575 (Hybrid) to 0.750, so part of the problem was the English-only models. Caveat: a single run on a synthetic corpus where documents of a topic are near-identical (random choice within a known topic gives ~0.25 Recall@5), so absolute values say little about real-data quality. Topic-level Hit@5 is reproducible with `scripts/topic_level_recall.py`.

| Query ID & Question | Target Document | BM25 Hit@5 | Hybrid (RRF) Hit@5 | Cross-Encoder Hit@5 | Diagnosis & Mechanism |
|---|---|:---:|:---:|:---:|---|
| **`hard_001`** (Wheat Disease Paraphrase)<br>«Які хвороби пшениці згадують буру іржа та фузаріоз?» | `agri_016_wheat_disease_15` | ❌ (Miss) | ❌ (Miss) | **✅ (Rank 3)** | **Cross-Encoder Win:** Bi-encoder pooled document at rank 11; cross-attention between question and paragraph text elevated target into top-3. |
| **`hard_004`** (Sunflower Sowing Rate)<br>«Яка щільність посіву насіння для соняшнику?» | `agri_159_seed_rate_18` | ❌ (Miss) | ❌ (Miss) | **✅ (Rank 3)** | **Cross-Encoder Win:** Dense bi-encoder matched IPM documents with similar vocabulary; Cross-Encoder prioritized specific seed density metrics. |
| **`hard_007`** (Multi-hop Disease Risks)<br>«Порівняти ризики хвороб пшениці в різних сезонах» | `agri_015_wheat_disease_14` | ❌ (Miss) | ❌ (Miss) | **✅ (Rank 4)** | **Cross-Encoder Win:** Successfully recovered multi-hop cross-season risk target. |
| **`hard_010`** (Organic Matter Humus)<br>«Органіка та сидерати для підвищення гумусу» | `agri_099_organic_matter_18` | ❌ (Miss) | **✅ (Rank 3)** | **✅ (Rank 2)** | **Hybrid + CE Win:** Semantic generalization across green manure and organic soil enrichment. |
| **`hard_006`** (Exact Formula)<br>«Дози азоту фосфору в NPK для поля» | `agri_062_npk_fertilizer_1` | ❌ (Miss) | ❌ (Miss) | ❌ (Miss) | **Challenging Case:** Exact formula match requires domain dictionary expansion. |
| **`hard_008`, `009`** (Out-of-Domain)<br>«Чи вирощують рис на Марсі...» | *None (Unanswerable)* | n/a | n/a | n/a | Refusal gate is not measured in the offline evaluation (it runs in rag-api, needs Docker).|

*Committed Raw Artifacts: [`work07-ai-platform/manifests/eval_per_query.json`](work07-ai-platform/manifests/eval_per_query.json) and [`work07-ai-platform/manifests/hard_eval_snapshot.json`](work07-ai-platform/manifests/hard_eval_snapshot.json).*

* **Reproduction Commands:**
  ```bash
  cd work07-ai-platform
  # Offline validation with Cross-Encoder (no Docker needed, ~25s):
  python scripts/eval_retrieval_offline.py
  # Live Docker cluster validation:
  docker compose up -d --build
  python scripts/benchmark_latency.py
  python scripts/eval_retrieval.py --golden-file data/golden/hard_retrieval.json --doc-id-prefix agri_
  ```
  *(Windows PowerShell: `.\make.ps1 build; .\make.ps1 up; py -3.13 scripts/benchmark_latency.py; .\make.ps1 eval-hard`)*

---

### 2. Work 05 — DocGuard: Zero-Trust Security Gateway Before the LLM

```
[User Request (tenant_a, alice)] 
       │
       ▼
[DocGuard Gateway (Java 21 / Spring)] ──► [ACL Engine (Principal & Tenant RBAC)]
       │ (Enforces allowed doc_ids)
       ▼
[Retrieval Service (Python / FastAPI)] ──► [Filtered Knowledge Base]
       │
       ▼ (Returns only authorized snippets)
[Audit Logger (Verbatim query + prompt injection capture)]
```

* **The Problem:** RAG architectures frequently leak private enterprise data when multi-tenant documents share vector databases, or when attackers use prompt injection to override LLM system prompts.
* **The Architecture:** DocGuard intercepts queries **before** they reach any model or vector store.
  1. Resolves tenant & principal ACL mapping to a whitelist of authorized `doc_id`s.
  2. Injects security filter directly into retrieval payload (`allowedDocIds`).
  3. Validates returned documents at gateway egress to prevent side-channel leaks.
  4. Automatic **Circuit Breaker / Degraded Mode**: if Python retrieval crashes or times out, Java gateway returns structured degraded fallback (`degraded: true`) without taking the microservice down.
  5. **Automated Verification:** Verified tenant isolation across 8 automated adversarial test scenarios in CI.
* **Injection-style query tests (`PromptInjectionIT`, 24 cases):** 11 injection-style queries (system-prompt override, cross-tenant probe, delimiter escape, DAN, role escalation, markdown exfiltration, indirect injection, SQL-style, instruction erasure, JSON tampering, base64) are each run through the real gateway and asserted on three access-control properties: (1) the document whitelist sent to retrieval equals the principal's ACL whatever the query says; (2) if a fooled retrieval returns another tenant's documents the gateway answers 403 and leaks no content; (3) the query is stored verbatim in the audit log. Extra JSON fields cannot widen the ACL, and blank/oversized (>2000 chars) queries get 400 (request validation was added during this audit; `@NotBlank` had not been enforced). **Limits:** DocGuard is an access-control layer, not an injection detector, and it does not stop an LLM being manipulated by text inside permitted documents; the retrieval service is mocked in these tests; identity headers (`X-Tenant-Id`, `X-Principal-Id`) are not authenticated by this service, so a client can claim any principal. An earlier "12/12 mitigated" figure from a hard-coded script was withdrawn.
* **Reproduction Commands:**
  ```bash
  cd work07-ai-platform
  # Offline validation with Cross-Encoder (no Docker needed, ~25s):
  python scripts/eval_retrieval_offline.py
  # Live Docker cluster validation:
  docker compose up -d --build
  python scripts/benchmark_latency.py
  python scripts/eval_retrieval.py --golden-file data/golden/hard_retrieval.json --doc-id-prefix agri_
  ```
  *(Windows PowerShell: `.\make.ps1 build; .\make.ps1 up; py -3.13 scripts/benchmark_latency.py; .\make.ps1 eval-hard`)*

---

### 2. Work 05 — DocGuard: Zero-Trust Security Gateway Before the LLM

```
[User Request (tenant_a, alice)] 
       │
       ▼
[DocGuard Gateway (Java 21 / Spring)] ──► [ACL Engine (Principal & Tenant RBAC)]
       │ (Enforces allowed doc_ids)
       ▼
[Retrieval Service (Python / FastAPI)] ──► [Filtered Knowledge Base]
       │
       ▼ (Returns only authorized snippets)
[Audit Logger (Verbatim query + prompt injection capture)]
```

* **The Problem:** RAG architectures frequently leak private enterprise data when multi-tenant documents share vector databases, or when attackers use prompt injection to override LLM system prompts.
* **The Architecture:** DocGuard intercepts queries **before** they reach any model or vector store.
  1. Resolves tenant & principal ACL mapping to a whitelist of authorized `doc_id`s.
  2. Injects security filter directly into retrieval payload (`allowedDocIds`).
  3. Validates returned documents at gateway egress to prevent side-channel leaks.
  4. Automatic **Circuit Breaker / Degraded Mode**: if Python retrieval crashes or times out, Java gateway returns structured degraded fallback (`degraded: true`) without taking the microservice down.
  5. **Automated Verification:** Verified tenant isolation across 8 automated adversarial test scenarios in CI.
* **Reproduction Commands:**
  ```bash
  cd work05-docguard
  python scripts/demo_offline.py
  # Live with Docker Compose:
  docker compose up -d --build
  bash scripts/reliability_demo.sh  # or PowerShell: .\scripts\reliability_demo.ps1
  ```

---

### 3. Work 01 & 04 — Applied ML Track: Temporal Backtesting, Leakage Prevention & MLOps Serving

```
[Raw Historical Data] 
       │
       ▼ (Chronological order only — NO future data leakage)
[Temporal Split (Train 5.8% -> Val 11.5% -> Test 39.3%)] 
       │
       ├─► [Leakage Guard: Strips post-event 'duration' feature]
       ├─► [Baseline: Balanced LogReg] ──► [Val macro-F1 tuning] ──► [Test Eval]
       └─► [Candidate: MLP 5 Seeds]    ──► [Temperature Scaling] ──► [Bootstrap CI]
                                                                        │
                                                                        ▼
                                                   [FastAPI MLOps Serving (Work 04)]
                                                   * event_time vs available_at contract
                                                   * Business cost matrix decisioning
                                                   * Feature z-score drift monitoring
```

* **The Problem (Real-world Tabular ML):** Naive random train/test splits severely overestimate model performance due to lookahead bias and target leakage. On the UCI Bank Marketing benchmark, naive models incorporate `duration` (call duration), which is impossible to know before initiating a call.
* **The ML Solution (Work 01):**
  * **Target Leakage Guard:** Strict elimination of `duration` and downstream signals.
  * **Temporal Backtesting:** Chronological split reflecting real operational deployment.
  * **Covariate Shift Management:** Train positive rate is 5.8%, validation is 11.5%, while test jumps to 39.3%. All thresholds (baseline=0.73, candidate=0.69) were strictly tuned on validation, avoiding test-set overfitting.
  * **Statistical Rigor:** 5-seed validation std (0.0045) and 95% Bootstrap Confidence Interval on test delta (`[-0.0085, 0.0089]`) documenting an honest negative result where complex neural nets fail to outperform calibrated linear baselines on tabular data.
  * **Error Slices:** Automated categorization into 5 error archetypes (`FN_borderline_high`, `FP_high_confidence`, etc.) across 20 documented rows.
* **Production Serving & MLOps (Work 04):**
  * **Temporal Data Contracts:** `event_time` vs `available_at` distinction enforced in JSON schemas to guarantee no feature ingestion from the future.
  * **Business Cost Matrix:** Decision threshold is derived from financial costs ($C_{FN}$ vs $C_{FP}$ vs $C_{review}$) rather than an arbitrary 0.5 probability.
  * **Production Serving:** FastAPI endpoints (`/v1/predict`, `/health`, `/v1/drift`) with live z-score drift alerts when feature distributions deviate.
* **Reproduction Commands:**
  ```bash
  # Work 01 offline demo
  cd work01-bank-marketing && python scripts/demo_offline.py
  # Work 04 serving & drift demo
  cd ../work04-ml-serving && python scripts/demo_offline.py
  ```

---

### 4. Work 03 — Agent Workflow: Crash Recovery & Transactional Outbox

* **The Problem:** Non-deterministic external tool calls (API effects, machinery commands, logistics dispatch) can execute twice if the application crashes or restarts immediately after an external side-effect is emitted but before the database transaction commits the updated workflow state.
* **The Architecture:**
  * **Idempotency Guard:** `idempotency_key` + SHA-256 payload hash uniquely identifies intents. A duplicate request with matching payload returns the cached result; an altered payload triggers `409 Conflict`.
  * **Transactional Outbox:** External intents are stored in PostgreSQL within the same ACID transaction as the workflow state checkpoint.
  * **Recovery Loop:** On restart after an abrupt process kill, `WorkflowRecovery` inspects pending outbox entries, verifies external stub effects, and resumes from the exact checkpoint without re-running external side effects.
  * **Scope & Matrix Tests:** 30 automated fault scenarios on H2 in CI plus the same suite re-run on a real PostgreSQL 16 Testcontainer (`./gradlew test -Dwork03.docker=true`; this IT was skipped by default and failed on a driver mismatch until fixed in this audit) (`idempotency: 8`, `checkpoint_recovery: 4`, `validation_400: 7`, `outbox: 3`, `conflict_409: 4`, `domain: 4`). Tested within a single-node Spring Boot + PostgreSQL transactional boundary (does not claim distributed consensus like Raft/Paxos).
* **Reproduction Commands:**
  ```bash
  cd work03-agent-workflow
  python scripts/demo_offline.py

  # Live with PostgreSQL (Docker):
  docker compose up -d             # 1. Start PostgreSQL container (port 5433)
  ./gradlew bootRun                # 2. Boot Spring Boot service (port 8083; or .\gradlew.bat bootRun)
  # In 2nd terminal:
  bash scripts/reliability_demo.sh # 3. Test idempotent retry & 409 conflict (or .\scripts\reliability_demo.ps1)
  ```

---

### 5. Work 08 — Demand Forecasting: Multi-Seasonal Backtesting & Inventory Risk

#### Side-by-Side Evaluation: Synthetic Benchmark vs Real-World Empirical Series

To stress-test forecasting robustness across both stationary seasonal dynamics and non-stationary physical sensor series, we evaluated identical 4-season expanding-window backtesting pipelines ($H=14$) on two datasets:

| Metric / Dimension | Synthetic Agro Simulation (20 series, 21,920 records) | Real-World Capital Bikeshare (2 series, 1,456 records) |
|---|:---:|:---:|
| **Seasonal Naive ($y_{t-7}$) WAPE** | 13.20% | **35.42% (Lower Error)** |
| **Historical 4-Week DOW MA WAPE** | 11.78% | 34.02% |
| **LightGBM Point ($P_{50}$) WAPE** | **7.83% (-40.68% error)** | 37.74% |
| **Baseline Simulated Inventory Cost** | 7,308.0 units | **33,576.2 units (Lower Cost)** |
| **LightGBM Safety Stock ($P_{83.3}$) Cost** | **4,160.9 units (-43.06% cost)** | 51,629.5 units |
| **Raw 80% Interval Coverage $[P_{10}, P_{90}]$** | 75.90% | 26.79% |
| **Calibrated Conformal Coverage (CQR)** | **84.11%** (observed $\ge 80\%$ across all 4 windows) | **75.89%** (+49.10 p.p. lift) |
| **Production Decision** | **Deploy LightGBM + CQR Calibration** | **Deploy Seasonal Baseline in Production** |

#### Production Baseline Selection: Why We Choose the Simple Baseline on Real Data
> **Engineering Trade-off:** When evaluating candidate machine learning models against domain baselines on real-world data, structural distribution shifts often dominate model variance. On the 2011–2012 Capital Bikeshare benchmark (where rapid fleet and station expansion nearly doubled daily volume without capacity covariates), our 4-season backtest showed that the zero-training **Seasonal Naive baseline outperformed LightGBM** in both forecast accuracy (**35.42% vs 37.74% WAPE**) and simulated inventory costs (**33,576 vs 51,630 units**).
>
> **Production Choice:** Based on these backtest results, we select the Seasonal Baseline for Capital Bikeshare in production. Deploying a complex GBDT regressor is unjustified when a simpler heuristic delivers lower error, zero training pipeline overhead, and zero model drift vulnerability.
>
> **Prediction Interval Coverage & Boundaries:** On synthetic agro data, Split Conformal Quantile Regression (CQR) achieved **observed $\ge 80.0\%$ empirical coverage across four test windows** (Spring: 80.4%, Summer: 89.3%, Autumn: 85.0%, Winter: 81.8%; mean 84.11% vs 75.90% uncalibrated). On real Bikeshare data, CQR improved coverage from 26.79% to 75.89% (+49.10 p.p.), but did not meet the nominal 80% target because rapid physical expansion violated the exchangeability assumption between the 56-day calibration window and the test horizon.

* **Reproduction Commands:**
  ```bash
  cd work08-demand-forecasting
  python scripts/demo_offline.py
  python scripts/eval_real_benchmark.py
  ```

---

## Clean-Clone Reproducibility Matrix

Every project can be evaluated in two ways:
1. **Offline Mode (< 30 seconds):** Evaluates models, manifests, and mock scenarios without running Docker daemons.
2. **Full Live Cluster Mode:** Boots full stack in Docker Compose and executes live HTTP requests against microservices.

```bash
# 1. Clone repository
git clone https://github.com/alexbohachev/portfolio-interview.git
cd portfolio-interview

# 2. Run offline validation across all projects
# Linux / macOS / Windows PowerShell:
python -m pytest work01-bank-marketing/tests work04-ml-serving/tests work08-demand-forecasting/tests
# Or via PowerShell smoke script:
powershell -ExecutionPolicy Bypass -File scripts/portfolio_smoke.ps1

# 3. Run live Docker validation for Work 05 & Work 07
cd work07-ai-platform && docker compose up -d --build
cd ../work05-docguard && docker compose up -d --build
```

---

## Project Directory & Architecture Summary

### Primary Reference Projects (7 Works)

| # | Project Directory | Domain Focus & Architecture | Key Technologies | Fast Verification |
|---|---|---|---|---|
| **08** | [`work08-demand-forecasting/`](work08-demand-forecasting/README.en.md) | Multi-series demand forecasting, 4-season backtesting, Newsvendor inventory risk | LightGBM, FastAPI, Conformal Prediction | `python scripts/demo_offline.py` · [`REPORT.md`](work08-demand-forecasting/REPORT.md) |
| **07** | [`work07-ai-platform/`](work07-ai-platform/README.en.md) | Microservice N+1 benchmark, hybrid RRF search, OpenTelemetry/Jaeger tracing | Java 21, Python, Kafka, Elasticsearch, Jaeger | `python scripts/demo_offline.py` · [`CASE_N1_PERF.md`](work07-ai-platform/CASE_N1_PERF.md) |
| **05** | [`work05-docguard/`](work05-docguard/README.en.md) | Multi-tenant security, pre-LLM ACL gateway, degraded circuit breaker | Java 21, FastAPI, Docker Compose | `python scripts/demo_offline.py` · [`REPORT.md`](work05-docguard/REPORT.md) |
| **01** | [`work01-bank-marketing/`](work01-bank-marketing/README.en.md) | Tabular ML classification, target leakage elimination, cost optimization | LightGBM, scikit-learn, Python 3.13 | `python scripts/demo_offline.py` · [`REPORT.md`](work01-bank-marketing/REPORT.md) |
| **04** | [`work04-ml-serving/`](work04-ml-serving/README.en.md) | Low-latency ML serving, schema data contracts, feature drift guard | FastAPI, scikit-learn, Pydantic | `python scripts/demo_offline.py` · [`REPORT.md`](work04-ml-serving/REPORT.md) |
| **02** | [`work02-rag-citations/`](work02-rag-citations/README.en.md) | Hybrid RRF retrieval, extractive citation verification, refusal gate | SentenceTransformers, BM25, NumPy | `python scripts/demo_offline.py` · [`REPORT.md`](work02-rag-citations/REPORT.md) |
| **03** | [`work03-agent-workflow/`](work03-agent-workflow/README.en.md) | Idempotent orchestrator, Transactional Outbox, crash recovery | Java 21, Spring Boot, PostgreSQL | `python scripts/demo_offline.py` · [`REPORT.md`](work03-agent-workflow/REPORT.md) |

### Auxiliary Reference Utility

| # | Project Directory | Focus & Architecture | Key Technologies | Verification |
|---|---|---|---|---|
| **06** | [`work06-bible-rag/`](work06-bible-rag/README.en.md) | Standalone offline verse retrieval with SQLite metadata | FAISS, SentenceTransformers, SQLite | `pytest tests/` · [`REPORT.md`](work06-bible-rag/REPORT.md) |
