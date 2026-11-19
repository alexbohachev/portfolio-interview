# Senior AI/ML Engineer — Portfolio Teardown & Engineering Evidence

[![CI: Clean-Clone Reproducibility (Run #44549558026 Passed)](https://img.shields.io/badge/CI_Run_44549558026-Passed-brightgreen)](https://github.com/alexbohachev/portfolio-interview/actions/runs/44549558026)
[![All GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI_Runs-blue)](https://github.com/alexbohachev/portfolio-interview/actions)
[![Demo Walkthrough (5-7 min)](https://img.shields.io/badge/Demo_Script-5--7_min_Interactive_Walkthrough-purple)](work07-ai-platform/DEMO_SCRIPT_5MIN.md#quick-visual-summary-for-recruiters)
[![Live Demo Runner](https://img.shields.io/badge/Live_Demo-scripts%2Flive__interview.ps1-orange)](scripts/live_interview.ps1)

> **Author:** Alex Bohachev  
> **Target Role:** Senior AI/ML Engineer / Senior AI Platform Engineer  
> **Core Focus:** Distributed AI & RAG Infrastructure · Applied Machine Learning & MLOps · High-Performance Backend Systems  
> **Repository:** Monorepo across Java 21, Python 3.13, Docker, Elasticsearch, Kafka, OpenTelemetry/Jaeger  

---

## 1. Executive Summary (The 2-Minute Recruiter Overview)

This portfolio documents **8 reproducible engineering projects and benchmarks** solving concrete challenges at the intersection of AI infrastructure, classical machine learning, and distributed reliability:

| Core Competency | Demonstrated In | Proven Capabilities & Engineering Impact | Honest Operational Boundaries (Scope) |
|---|---|---|---|
| **Demand Forecasting & Risk Modeling** | **Work 08 (Demand Forecasting)** | Supply chain demand forecasting benchmark (20 series, 21,920 daily samples). **Strict 4-season expanding-window backtesting ($H=14$, isolated series rolling, ex-ante feature alignment)**. On synthetic agro-demand, LightGBM achieves **40.68% WAPE reduction vs Seasonal Naive** (7.83% vs 13.20%) and Newsvendor critical ratio optimization ($\tau^* = 83.33\%$) cuts inventory costs by **43.06%**, with Split Conformal Quantile Regression (CQR) delivering **observed $\ge 80.0\%$ coverage across four synthetic test windows** (**mean 84.11%** vs 75.90% uncalibrated). On real empirical sensor series (Capital Bikeshare 2011–2012), CQR lifts coverage from 26.79% to 75.89%, while Seasonal Naive beats LightGBM (35.42% vs 37.74% WAPE) — and **we explicitly choose the Seasonal Baseline for production**. FastAPI serving with ~60 ms latency and calibrated intervals. | Calibrated simulation benchmark + real empirical sensor benchmark; direct forecasting model locked to operational horizon $H=14$. |
| **Distributed Performance & Latency** | **Work 07 (AI Platform)** | Eliminated **N+1 HTTP calls** from Java microservices to Python RAG API. Reduced **p95 latency from ~196 ms → ~47 ms (4.19× speedup, p50 5.06×)**, verified via OpenTelemetry/Jaeger distributed tracing and committed raw sample arrays. | Local Docker Compose microservice stand; not a multi-region geo-distributed Kubernetes cluster. |
| **Enterprise AI Security & Governance** | **Work 05 (DocGuard)** | Zero-Trust Pre-LLM Security Gateway. Enforces multi-tenant principal ACL filtering **before** documents reach LLM or vector search. **100% tenant isolation across 8 security scenarios**, verbatim prompt injection audit logging, automated degraded mode. | In-memory ACL cache with REST eviction; not an external enterprise identity provider (Ory/Keycloak). |
| **Applied ML & Temporal Backtesting** | **Work 01 (Bank Marketing)** | Empirically rigorous tabular ML on real UCI data. Strict **target leakage elimination** (removed post-call `duration`), chronological temporal backtesting, honest handling of severe covariate shift (5.8% → 39.3%), bootstrap confidence intervals. | Tabular UCI dataset; temperature scaling does not completely eliminate covariate shift without domain adaptation. |
| **Production ML Serving & MLOps** | **Work 04 (Risk Serving)** | Low-latency FastAPI model serving. Explicit data contracts separating `event_time` from `available_at`, **business cost matrix optimization** (FP/FN/review cost), calibrated LightGBM, and live feature drift detection via z-score monitoring. | Evaluated on streaming event batches; enterprise production requires an external feature store connector. |
| **Search & Retrieval Science** | **Work 02 & 07 (RAG Science)** | Hybrid search combining **dense kNN embeddings and BM25 via Reciprocal Rank Fusion (RRF)**. Evaluated on hard paraphrases; calibrated refusal threshold gate preventing hallucinations on unanswerable queries. | 200 domain documents; fine-grained topical clusters motivate testing a 2nd-stage Cross-Encoder re-ranker to improve discrimination beyond bi-encoder retrieval. |
| **Distributed Systems Resilience** | **Work 03 (Agent Workflow)** | Deterministic 3-step orchestrator with **Transactional Outbox and Checkpoint recovery**. Survives abrupt process crashes between external side effects and transaction commits without duplicate external effects (**30/30 fault scenarios passing**); detects payload tampering with HTTP 409 Conflict. | Scoped to single-node Spring Boot transactional boundary with PostgreSQL; does not claim multi-node consensus like Raft/Paxos. |

---

## 2. The 10-Minute Technical Deep Dive (For Engineering Leads & Architects)

### Case Study 1: Work 07 — Distributed RAG Platform & N+1 Latency Fix

#### The Problem
In high-throughput microservice ecosystems, naive integration between backend application services and AI retrieval services often introduces sequential query amplification. In our logistics microservice, creating an equipment request triggered an N+1 retrieval pattern: the incoming question was tokenized in Java, and sequential HTTP calls were made to Python `rag-api` for each individual token.

#### Architectural Diagnosis in Jaeger
Distributed traces in Jaeger (`http://localhost:16687`) exposed a cascading waterfall of 6 sequential spans to `/v1/knowledge/search` per single user request, causing local p95 to spike to **~196 ms**.

```
[Client Request]
       │
       ▼
[Logistics Microservice (Java 21 / Spring Boot 3)]
       │
       ├──► (Before: N+1 calls) ──► HTTP /v1/knowledge/search (token 1)
       │                        ──► HTTP /v1/knowledge/search (token 2)
       │                        ──► HTTP /v1/knowledge/search (token 3) [Latency p95 = 195.7 ms]
       │
       └──► (After: Single Batch) ──► HTTP /v1/knowledge/search (TopK=3, Mode=hybrid)
                                          │
                                          ▼
                             [Python 3.13 / FastAPI RAG API]
                                          │
                                          ▼
                         [Elasticsearch 8.17 (RRF: BM25 + kNN)] [Latency p95 = 46.7 ms]
```

#### The Engineering Fix
Replaced the iterative token-loop with a single batch hybrid call (`EquipmentSearchService.searchFast()`), requesting Top-K results directly. Python `rag-api` executes Reciprocal Rank Fusion (RRF) between dense kNN vector search and BM25 full-text search directly inside Elasticsearch.

#### Quantitative Benchmarking Across Independent Runs (25 samples per profile):
* **Run 1 (Baseline, 2026-11-18, Git SHA `6efad68`):**
  * `slow` profile (N+1): p50 = **172.6 ms** | **p95 = 197.0 ms**
  * `fast` profile (batch hybrid): p50 = **34.0 ms** | **p95 = 53.3 ms**
  * Artifact: `work07-ai-platform/manifests/latency_snapshot.json`
* **Run 2 (Clean Clone Verification, 2026-11-19, Git SHA `45d550c`):**
  * `slow` profile (N+1): p50 = **171.6 ms** | **p95 = 195.7 ms** | mean = 179.2 ms
  * `fast` profile (batch hybrid): p50 = **33.9 ms** | **p95 = 46.7 ms** | mean = 37.9 ms
  * Artifact: `work07-ai-platform/artifacts/latency_before_after.json` & `latency_raw_samples.json`
* **Net Performance Gain:** **5.06×–5.08× speedup at p50, 3.70×–4.19× speedup at p95** (~75% reduction in overall latency).
* **Committed Raw Evidence:**
  * Raw timing arrays (all 25 samples per profile): [`work07-ai-platform/manifests/latency_raw_samples.json`](work07-ai-platform/manifests/latency_raw_samples.json) / [`artifacts/latency_raw_samples.json`](work07-ai-platform/artifacts/latency_raw_samples.json)
  * Summary metrics: [`work07-ai-platform/manifests/latency_before_after.json`](work07-ai-platform/manifests/latency_before_after.json) / [`artifacts/latency_before_after.json`](work07-ai-platform/artifacts/latency_before_after.json)

#### Hard Retrieval Evaluation: Hybrid RRF vs BM25 Breakdown (`eval-hard`)
Standard synthetic tests give a trivial `Recall@5 = 1.0`. To test real retrieval limits, we evaluated on **hard paraphrases, multi-hop queries, and unanswerable prompts** (`data/golden/hard_retrieval.json`, scoped via `--doc-id-prefix agri_` to the 200 documents shared with Work 02):

| Query ID & Question | Target Document | BM25 Hit@5 | Hybrid (RRF) Hit@5 | Retrieval Outcome & Diagnosis |
|---|---|:---:|:---:|---|
| **`hard_007`** (Multi-hop)<br>«Порівняти ризики хвороб пшениці в різних сезонах» | `agri_015_wheat_disease_14` | ❌ (Miss) | **✅ (Rank 4)** | **Hybrid Wins (+1):** Semantic generalization across seasonal disease risks where BM25 lacks exact vocabulary. |
| **`hard_006`** (Exact Formula)<br>«Дози азоту фосфору в NPK для поля» | `agri_062_npk_fertilizer_1` | **✅ (Rank 2)** | ❌ (Miss) | **BM25 Wins (+1):** Exact keyword specificity. BM25 directly matched the specific NPK formula ratio. |
| **`hard_001`–`005`, `010`** (Dense Clusters)<br>Synonym paraphrases on IPM, seed rate, soil pH | Topic-specific targets | ❌ (Cluster tie) | ❌ (Cluster tie) | **Tie:** Both systems pulled topically relevant clusters, showing that bi-encoder retrieval identifies topic groups; a 2nd-stage Cross-Encoder re-ranker is the natural next hypothesis to evaluate for fine-grained ranking. |
| **`hard_008`, `009`** (Out-of-Domain)<br>«Чи вирощують рис на Марсі...» | *None (Unanswerable)* | **Filtered** | **Filtered** | **Hallucination Gate:** Pre-retrieval refusal gate aborted unanswerable queries before generation. |

*Committed Raw Artifacts: [`work07-ai-platform/manifests/eval_per_query.json`](work07-ai-platform/manifests/eval_per_query.json) / [`artifacts/eval_per_query.json`](work07-ai-platform/artifacts/eval_per_query.json) and [`manifests/hard_eval_snapshot.json`](work07-ai-platform/manifests/hard_eval_snapshot.json).*

---

### Case Study 2: Work 05 — DocGuard: Zero-Trust Pre-LLM Security Gateway

#### The Problem
Enterprise generative AI systems commonly suffer from cross-tenant data leaks and prompt injection exploits when multiple customers or roles share an indexing backend. Relying on LLM system prompts for data security is inherently fragile.

#### The Architecture
DocGuard introduces an independent Java 21 security reverse gateway positioned in front of the Python retrieval service:

```
[Inbound Query: tenant_a:alice]
       │
       ▼
[DocGuard Gateway (Java 21)] ──► [ACL Engine: Resolves tenant_a allowed doc_ids]
       │ (Rewrites request: allowedDocIds = [agri_001, agri_003, ...])
       ▼
[Retrieval Service (Python FastAPI)] ──► [Filtered Vector/BM25 Index]
       │
       ▼ (Returns only authorized candidate snippets)
[DocGuard Gateway Post-Filter Validation] ──► [Structured Response to Client]
       │
       ▼
[Audit Repository: Logs verbatim user query, including adversarial prompt injections]
```

#### Security Highlights
1. **Zero-Trust Document Whitelisting:** Even if a vector search returns an unauthorized document, the gateway blocks it (`403 Forbidden`) before it reaches the caller or prompt context.
2. **Dynamic ACL Invalidation:** Admin endpoint `/api/v1/admin/invalidate-cache` immediately forces cache eviction and re-evaluates ACLs.
3. **Resilience & Degraded Mode:** If the Python retrieval container crashes or fails to respond within 10 seconds, the Java gateway gracefully degrades to returning `{ "degraded": true, "hits": [] }`, preventing microservice cascading failures.

---

### Case Study 3: Work 01 & Work 04 — Senior Applied ML & MLOps Pipeline

#### The Problem (Common Tabular ML Pitfalls)
Standard academic pipelines use random train/test splits, which introduce temporal lookahead bias and overestimate real-world performance. Furthermore, on benchmarks like UCI Bank Marketing, models frequently leak the `duration` feature (call length), which is unknown prior to placing the call.

#### The ML Rigor (Work 01)
1. **Target Leakage Guard:** Strict programmatic removal of `duration` and post-call features.
2. **Temporal Split & Severe Covariate Shift:** Chronological splitting partitioning data into Train (5.8% positive rate), Validation (11.5% positive rate), and Test (39.3% positive rate). All decision thresholds (baseline 0.73, candidate 0.69) were strictly tuned on validation.
3. **Calibrated Probabilities & Bootstrap CI:** Candidate MLP with temperature scaling vs Balanced Logistic Regression baseline. Bootstrap 95% Confidence Interval on test macro-F1 delta (`[-0.0085, 0.0089]`) proved an honest negative result — demonstrating that complex neural architectures did not offer statistically significant gains over linear baselines on this tabular distribution.
4. **Error Segmentation:** Categorized test errors into 5 actionable clusters (e.g. `FN_borderline_high`, `FP_high_confidence`).

#### Production ML Serving & Drift (Work 04)
1. **Temporal Data Contracts:** JSON schemas explicitly differentiate `event_time` (when transaction occurred) from `available_at` (when feature was ingested), preventing lookahead bias during feature stores retrieval.
2. **Business Cost Matrix Optimization:**
   $$\text{Total Cost} = C_{FN} \cdot FN + C_{FP} \cdot FP + C_{review} \cdot \text{Review}$$
   Decision boundary is dynamically mapped to financial ROI rather than an arbitrary 0.5 probability.
3. **FastAPI Serving & Drift Monitoring:** Endpoints `/v1/predict`, `/health`, and `/v1/drift`. Live z-score calculation alerts when production feature distributions drift away from training baselines.

---

### Case Study 4: Work 03 — Fault-Tolerant Distributed Workflow Orchestration

#### The Problem
In distributed workflow systems, non-deterministic external tool calls (API effects, machinery commands, logistics dispatch) can execute twice if the application crashes or restarts immediately after an external side-effect is emitted but before the database transaction commits the updated workflow state.

#### The Architecture
* **Idempotency Guard:** Every workflow execution requires an `idempotency_key` and SHA-256 command hash. Retrying with identical parameters safely returns the cached result; retrying with altered parameters returns `409 Conflict`.
* **Transactional Outbox:** Intent to call external services is written to PostgreSQL inside the same atomic database transaction as the workflow state checkpoint.
* **Crash Recovery Loop:** If the node crashes after an external side-effect is recorded, `WorkflowRecovery` verifies existing effects on startup, completes the pending checkpoint, and marks the workflow `COMPLETED` without re-issuing duplicate external calls.
* **Scope & Matrix Tests:** 30 automated fault injection scenarios verified in CI (`idempotency: 8`, `checkpoint_recovery: 4`, `validation_400: 7`, `outbox: 3`, `conflict_409: 4`, `domain: 4`). Tested within a single-node Spring Boot + PostgreSQL transactional boundary (does not claim distributed consensus like Raft/Paxos).

---

### Case Study 4: Work 08 — End-to-End Demand Forecasting & Inventory Risk Optimization

#### Business Formulation & Asymmetric Risk
In supply chain networks, forecasting errors carry highly asymmetric costs: stockouts during seasonal application windows penalize the business heavily ($C_{under} = 5.0$), while inventory holding and spoilage penalties are lower ($C_{over} = 1.0$). Optimal service level demands the **Newsvendor critical fractile** $\tau^* = \frac{C_{under}}{C_{under} + C_{over}} = 83.33\%$. Point forecasting at the median ($P_{50}$) leads to structural inventory deficits.

#### Strict 4-Season Chronological Expanding Backtesting
* **Data Scale & Nature:** 21,920 daily records across 20 distinct time series (5 regional distribution hubs $\times$ 4 agricultural product lines) spanning 3 full years. Formatted as a calibrated simulation benchmark with authentic agro-seasonal dynamics for 100% autonomous CI reproducibility without external data dropouts.
* **Target Leakage Elimination & Series Isolation:** For forecast horizon $H = 14$ days, all lag steps are shifted to $t - 14$ or earlier ($lag_{14}, lag_{21}, lag_{28}, lag_{35}$). All rolling statistics (windows 7, 14, 28) are computed strictly on data prior to $t - 14$ via grouped transforms, preventing cross-series boundary contamination.
* **Ex-Ante Feature Alignment & Zero Skew:** Shared `build_ex_ante_features` pipeline ensures backtesting features exactly mirror production inference features at cutoff $T_0$ (last known price persistence, noise-free seasonal climatological temperature harmonic, planned promo schedule).
* **Multi-Seasonal Coverage:** 4 sequential expanding-window folds covering all 4 operational agro-seasons (Spring Sowing Peak, Summer Crop Protection, Autumn Harvest & Sowing, Winter Baseline).

#### Side-by-Side Evaluation: Synthetic Benchmark vs Real-World Empirical Series

To stress-test forecasting robustness across both stationary seasonal domains and non-stationary physical sensor series, we evaluated identical 4-season expanding-window backtesting pipelines ($H=14$) on two datasets:

| Metric / Dimension | Synthetic Agro Simulation (20 series, 21,920 records) | Real-World Capital Bikeshare (2 series, 1,456 records) |
|---|:---:|:---:|
| **Seasonal Naive ($y_{t-7}$) WAPE** | 13.20% | **35.42% (Winner)** |
| **Historical 4-Week DOW MA WAPE** | 11.78% | 34.02% |
| **LightGBM Point ($P_{50}$) WAPE** | **7.83% (-40.68% error)** | 37.74% |
| **Baseline Simulated Inventory Cost** | 7,308.0 units | **33,576.2 units (Winner)** |
| **LightGBM Safety Stock ($P_{83.3}$) Cost** | **4,160.9 units (-43.06% cost)** | 51,629.5 units |
| **Raw 80% Interval Coverage $[P_{10}, P_{90}]$** | 75.90% | 26.79% |
| **Calibrated Conformal Coverage (CQR)** | **84.11%** (observed $\ge 80\%$ across all 4 windows) | **75.89%** (+49.10 p.p. lift) |
| **Senior ML Production Decision** | **Deploy LightGBM + CQR Calibration** | **Deploy Seasonal Baseline in Production** |

#### Senior ML Engineering Decision: Why We Choose the Simple Baseline for Bikeshare
> **The Senior ML Takeaway:** When evaluating candidate machine learning architectures against strong domain baselines, real-world data often exhibits structural shifts — here, massive network expansion in Washington D.C. throughout 2011–2012 that nearly doubled daily volume without available fleet capacity features. In our 4-season chronological backtest, the zero-training **Seasonal Naive baseline outperformed LightGBM** both in forecast accuracy (**35.42% vs 37.74% WAPE**) and in simulated business inventory costs (**33,576 vs 51,630 units**).
>
> A Senior ML Engineer does not deploy a complex GBDT regressor when a simple domain heuristic outperforms it. **For Capital Bikeshare in production, we choose the Seasonal Baseline**. This eliminates model training pipelines, feature store latency, and model drift monitoring overhead, while providing an honest performance baseline.
>
> Regarding prediction intervals, on synthetic agro data Split Conformal Quantile Regression delivered **observed $\ge 80.0\%$ coverage across four synthetic test windows** (**80.4% Spring, 89.3% Summer, 85.0% Autumn, 81.8% Winter; mean 84.11%** vs 75.90% uncalibrated). On real Bikeshare data, CQR substantially lifted empirical coverage from **26.79% to 75.89%**; however, it remained below the nominal 80% target because rapid capacity expansion violated the exchangeability assumption between the trailing 56-day calibration window and the forward 14-day test horizon. This demonstrates an honest, senior-level understanding of conformal calibration boundaries under distribution shift.

#### Multi-Season Stability & Serving
* **Multi-Season Stability:** In agro operations, LightGBM WAPE remains tightly bounded between **7.60% and 7.98% across all 4 seasons**, whereas seasonal baseline degrades to 16.92% during seasonal transitions.
* **Production Serving:** Low-latency FastAPI serving (`POST /v1/forecast`, `GET /v1/health`) delivers 14-day forecasts with calibrated quantiles in **~55–65 ms** under a strict $H=14$ operational contract with support for planned promo schedules. Full technical case study: [`REPORT.md`](work08-demand-forecasting/REPORT.md).

---

## 3. Technology Stack Matrix

| Layer | Technologies Used |
|---|---|
| **Programming Languages** | Java 21 (LTS), Python 3.13 |
| **Backend & Microservices** | Spring Boot 3, Spring Web / RestClient, FastAPI, Uvicorn, Pydantic v2 |
| **Machine Learning & AI** | PyTorch, SentenceTransformers (`all-MiniLM-L6-v2`), scikit-learn, LightGBM, FAISS, NumPy, joblib |
| **Search & Information Retrieval** | Elasticsearch 8.17 (BM25 + kNN dense vector search + RRF fusion) |
| **Event Streaming & Databases** | Apache Kafka / Redpanda, PostgreSQL 16, SQLite |
| **Observability & Telemetry** | OpenTelemetry Java Agent, OpenTelemetry Python SDK, Jaeger UI |
| **DevOps, Packaging & CI** | Docker Compose, GitHub Actions (multi-platform: Windows + Ubuntu runners) |

---

## 4. How to Verify (Clean-Clone Reproducibility)

The monorepo is engineered to be 100% reproducible from a clean machine:

```powershell
# 1. Clone the repository
git clone https://github.com/alexbohachev/portfolio-interview.git
cd portfolio-interview

# 2. Run the offline validation suite (< 30 seconds, no Docker required)
.\scripts\repro_check.ps1

# 3. Run the live Docker validation suite (Work 05 DocGuard + Work 07 AI Platform)
.\scripts\repro_check.ps1 -Docker

# 4. Run the Work 07 flagship N+1 latency benchmark live
cd work07-ai-platform
py -3.13 scripts/benchmark_latency.py

# 5. Run the Work 05 DocGuard multi-tenant reliability & security demo
cd ../work05-docguard
.\scripts\reliability_demo.ps1
```
