# Senior AI/ML Engineer — Portfolio Teardown

[![CI: Clean-Clone Reproducibility (Run #44543672145 Passed)](https://img.shields.io/badge/CI_Run_44543672145-Passed-brightgreen)](https://github.com/alexbohachev/portfolio-interview/actions/runs/44543672145)
[![All GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI_Runs-blue)](https://github.com/alexbohachev/portfolio-interview/actions)
[![Demo Walkthrough (5-7 min)](https://img.shields.io/badge/Demo_Recording-5--7_min_Walkthrough-purple)](work07-ai-platform/DEMO_SCRIPT_5MIN.md#quick-visual-summary-for-recruiters)
[![Live Demo Runner](https://img.shields.io/badge/Live_Demo-scripts%2Flive__interview.ps1-orange)](scripts/live_interview.ps1)

Hardened engineering monorepo of **8 reproducible reference projects and benchmarks** demonstrating dual-track mastery: **Distributed AI/RAG Infrastructure** (Java 21, Python 3.13, Docker, Kafka, OpenTelemetry) and **Applied Machine Learning / MLOps** (temporal backtesting, target leakage prevention, probability calibration, production serving, drift detection).

> **Ukrainian documentation:** [`README.md`](README.md) · **Repro guide:** [`REPRO.md`](REPRO.md) · **Interview prep:** [`INTERVIEW_PREP.md`](INTERVIEW_PREP.md) · **N+1 case study:** [`CASE_N1_PERF.md`](work07-ai-platform/CASE_N1_PERF.md) · **Live demo script:** [`DEMO_SCRIPT_5MIN.md`](work07-ai-platform/DEMO_SCRIPT_5MIN.md) · **Standalone guide:** [`STANDALONE_PORTFOLIO.md`](STANDALONE_PORTFOLIO.md)

---

## 2-Minute Recruiter Summary: Capabilities & Honest Boundaries

Every claim below is backed by committed test suites, committed raw latency arrays, and automated fault matrix tests in CI:

| Dimension | Proof in Monorepo | Proven Capabilities & Engineering Impact | Honest Operational Boundaries (Scope) |
|---|---|---|---|
| **AI Systems & Performance** | **Work 07 (AI Platform)** | Eliminated N+1 microservice calls Java → Python RAG API. **p95 latency reduced from ~196 ms → ~47 ms (4.19× speedup, p50 5.06×)**; confirmed via OpenTelemetry/Jaeger traces and committed raw samples. | Local Docker Compose microservice stand; not a multi-region geo-distributed Kubernetes cluster. |
| **Enterprise AI Security** | **Work 05 (DocGuard)** | Zero-trust Pre-LLM gateway (Java 21 + FastAPI). Intercepts queries before vector DB or LLM. **100% tenant isolation across 8 security vectors**, verbatim prompt injection logging, degraded circuit-breaker fallback. | In-memory ACL cache with REST eviction; not an external enterprise identity provider (Ory/Keycloak). |
| **Applied ML & Backtesting** | **Work 01 (Bank Marketing)** | Empirically rigorous tabular ML on real UCI data. **Strict target leakage elimination** (removed post-call `duration`), chronological temporal backtesting under severe covariate shift (5.8% → 39.3%), bootstrap 95% CI. | Tabular UCI dataset; temperature scaling does not completely eliminate covariate shift without domain adaptation. |
| **Demand Forecasting & Risk** | **Work 08 (Demand Forecasting)** | End-to-end multi-series supply chain demand forecasting (20 series, 21,920 samples). **Zero-leakage 4-fold rolling backtesting ($H=14$)**. LightGBM achieves **38.7% WAPE reduction vs Seasonal Naive baseline** (7.23% vs 11.79%). Newsvendor asymmetric critical fractile ($\tau^* = 83.33\%$) cuts stockout/holding costs by **49.70%**. FastAPI production serving with ~64 ms latency. | Tabular multi-series with daily discretization; without real-time streaming Kafka connectors. |
| **Production ML Serving & Drift** | **Work 04 (Risk Serving)** | Low-latency FastAPI model serving. Explicit **data contracts (`event_time` vs `available_at`)**, business cost matrix thresholding ($C_{FN}$ vs $C_{FP}$ vs $C_{review}$), and live z-score feature drift alerts. | Evaluated on streaming event batches; enterprise production requires an external feature store connector. |
| **Distributed Resilience** | **Work 03 (Agent Workflow)** | Deterministic 3-step orchestrator with **Transactional Outbox and Checkpoint recovery**. Survived **30/30 automated fault injection scenarios** without duplicate external effects; returns HTTP 409 Conflict on payload tampering. | Scoped to single-node Spring Boot transactional boundary with PostgreSQL; does not claim multi-node consensus like Raft/Paxos. |
| **Search & Retrieval Science** | **Work 02 & 07 (RAG Science)** | Hybrid RRF search (Elasticsearch BM25 + dense kNN). **Evaluated on hard paraphrases and multi-hop queries**; calibrated pre-retrieval refusal gate preventing hallucinations on unanswerable prompts. | 200 domain documents; fine-grained topical clusters motivate testing a 2nd-stage Cross-Encoder re-ranker to improve discrimination beyond bi-encoder retrieval. |
| **Full Stack Competence** | **Monorepo Suite** | Java 21 (Spring Boot 3, RestClient), Python 3.13 (FastAPI, PyTorch/SentenceTransformers), Docker, Kafka, Elasticsearch, Jaeger. | Multi-platform CI runs Windows offline suite (<30s) + Ubuntu Docker integration suite. |

---

## 10-Minute Engineering Deep Dive: Core Cases

### 1. Work 07 — Distributed AI Platform & N+1 Latency Elimination (Primary Case)

```
[Client / Mobile App]
       │
       ▼
[Logistics Service (Java 21)] ──(Trace: OpenTelemetry)──► [Jaeger UI :16687]
       │
       ├─► (Before: N+1 calls per token) ──┐
       │                                  ▼
       └─► (After: Single hybrid call) ──► [RAG API (Python 3.13 / FastAPI)]
                                                 │
                                                 ▼
                                     [Elasticsearch 8.17 (BM25 + kNN / RRF)]
```

* **Root Cause Discovered in Jaeger:** During high-load testing of `POST /api/v1/equipment-requests`, Jaeger traces revealed that the logistics service split incoming query text into individual tokens and issued sequential HTTP requests back-and-forth to Python `rag-api`.
* **Architectural Fix:** Replaced iterative search with a single batch hybrid call (`searchFast()`) requesting top-K items via Reciprocal Rank Fusion (RRF) in Elasticsearch.
#### Quantitative Benchmarking Across Independent Runs (25 samples per profile):

* **Run 1 (Baseline, 2026-11-18, Git SHA `6efad68`):**
  * `slow` profile (N+1): p50 = **172.6 ms** | **p95 = 197.0 ms**
  * `fast` profile (batch hybrid): p50 = **34.0 ms** | **p95 = 53.3 ms**
  * Artifact: `work07-ai-platform/manifests/latency_snapshot.json`
* **Run 2 (Clean Clone Verification, 2026-11-19, Git SHA `45d550c`):**
  * `slow` profile (N+1): p50 = **171.6 ms** | **p95 = 195.7 ms** | mean = 179.2 ms
  * `fast` profile (batch hybrid): p50 = **33.9 ms** | **p95 = 46.7 ms** | mean = 37.9 ms
  * Artifact: `work07-ai-platform/artifacts/latency_before_after.json` & `latency_raw_samples.json`
* **Net Performance Gain:** **5.06×–5.08× speedup at p50, 3.70×–4.19× speedup at p95** (~75% reduction in latency).
* **Committed Raw Evidence:**
  * Raw timing arrays (all 25 samples per profile): [`manifests/latency_raw_samples.json`](work07-ai-platform/manifests/latency_raw_samples.json) / [`artifacts/latency_raw_samples.json`](work07-ai-platform/artifacts/latency_raw_samples.json)
  * Summary metrics: [`manifests/latency_before_after.json`](work07-ai-platform/manifests/latency_before_after.json) / [`artifacts/latency_before_after.json`](work07-ai-platform/artifacts/latency_before_after.json)

#### Hard Retrieval Evaluation: Hybrid RRF vs BM25 Trade-offs

Standard synthetic tests give a trivial `Recall@5 = 1.0`. To test real retrieval limits, we evaluated on **hard paraphrases, multi-hop queries, and unanswerable prompts** (`data/golden/hard_retrieval.json`, scoped via `--doc-id-prefix agri_` to the 200 documents shared with Work 02):

| Query ID & Question | Target Document | BM25 Hit@5 | Hybrid (RRF) Hit@5 | Retrieval Outcome & Diagnosis |
|---|---|:---:|:---:|---|
| **`hard_007`** (Multi-hop)<br>«Порівняти ризики хвороб пшениці в різних сезонах» | `agri_015_wheat_disease_14` | ❌ (Miss) | **✅ (Rank 4)** | **Hybrid Wins (+1):** Semantic generalization across seasonal disease risks where BM25 lacks exact vocabulary. |
| **`hard_006`** (Exact Formula)<br>«Дози азоту фосфору в NPK для поля» | `agri_062_npk_fertilizer_1` | **✅ (Rank 2)** | ❌ (Miss) | **BM25 Wins (+1):** Exact keyword specificity. BM25 directly matched the specific NPK formula ratio. |
| **`hard_001`–`005`, `010`** (Dense Clusters)<br>Synonym paraphrases on IPM, seed rate, soil pH | Topic-specific targets | ❌ (Cluster tie) | ❌ (Cluster tie) | **Tie:** Both systems pulled topically relevant clusters, showing that bi-encoder retrieval identifies topic groups; a 2nd-stage Cross-Encoder re-ranker is the natural next hypothesis to evaluate for fine-grained ranking. |
| **`hard_008`, `009`** (Out-of-Domain)<br>«Чи вирощують рис на Марсі...» | *None (Unanswerable)* | **Filtered** | **Filtered** | **Hallucination Gate:** Pre-retrieval refusal gate aborted unanswerable queries before generation. |

*Committed Raw Artifacts: [`manifests/eval_per_query.json`](work07-ai-platform/manifests/eval_per_query.json) / [`artifacts/eval_per_query.json`](work07-ai-platform/artifacts/eval_per_query.json) and [`manifests/hard_eval_snapshot.json`](work07-ai-platform/manifests/hard_eval_snapshot.json).*

* **Verification Command:**
  ```powershell
  cd work07-ai-platform
  .\make.ps1 build; .\make.ps1 up
  py -3.13 scripts/benchmark_latency.py
  .\make.ps1 eval-hard
  ```

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
* **Verification Command:**
  ```powershell
  cd work05-docguard
  docker compose up -d --build
  .\scripts\reliability_demo.ps1
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
* **The Rigorous ML Solution (Work 01):**
  * **Target Leakage Guard:** Strict elimination of `duration` and downstream signals.
  * **Temporal Backtesting:** Chronological split reflecting real operational deployment.
  * **Covariate Shift Management:** Train positive rate is 5.8%, validation is 11.5%, while test jumps to 39.3%. All thresholds (baseline=0.73, candidate=0.69) were strictly tuned on validation, avoiding test-set overfitting.
  * **Statistical Rigor:** 5-seed validation std (0.0045) and 95% Bootstrap Confidence Interval on test delta (`[-0.0085, 0.0089]`) documenting an honest negative result where complex neural nets fail to outperform calibrated linear baselines on tabular data.
  * **Slices & Error Cases:** Automated categorization into 5 error archetypes (`FN_borderline_high`, `FP_high_confidence`, etc.) across 20 documented rows.
* **Production Serving & MLOps (Work 04):**
  * **Temporal Data Contracts:** `event_time` vs `available_at` distinction enforced in JSON schemas to guarantee no feature ingestion from the future.
  * **Business Cost Matrix:** Decision threshold is derived from financial costs ($C_{FN}$ vs $C_{FP}$ vs $C_{review}$) rather than arbitrary 0.5 probability.
  * **Production Serving:** FastAPI endpoints (`/v1/predict`, `/health`, `/v1/drift`) with live z-score drift alerts when feature distributions deviate.
* **Verification Command:**
  ```powershell
  # Work 01 offline demo
  cd work01-bank-marketing; py -3.13 scripts/demo_offline.py
  # Work 04 serving & drift demo
  cd ../work04-ml-serving; py -3.13 scripts/demo_offline.py
  ```

---

### 4. Work 03 — Agent Workflow: Crash Recovery & Transactional Outbox

* **The Problem:** Non-deterministic external tool calls (API effects, machinery commands, logistics dispatch) can execute twice if the application crashes or restarts immediately after an external side-effect is emitted but before the database transaction commits the updated workflow state.
* **The Architecture:**
  * **Idempotency Guard:** `idempotency_key` + SHA-256 payload hash uniquely identifies intents. A duplicate request with matching payload returns the cached result; an altered payload triggers `409 Conflict`.
  * **Transactional Outbox:** External intents are stored in PostgreSQL within the same ACID transaction as the workflow state checkpoint.
  * **Recovery Loop:** On restart after an abrupt process kill, `WorkflowRecovery` inspects pending outbox entries, verifies external stub effects, and resumes from the exact checkpoint without re-running external side effects.
  * **Scope & Matrix Tests:** 30 automated fault scenarios verified in CI (`idempotency: 8`, `checkpoint_recovery: 4`, `validation_400: 7`, `outbox: 3`, `conflict_409: 4`, `domain: 4`). Tested within a single-node Spring Boot + PostgreSQL transactional boundary (does not claim distributed consensus like Raft/Paxos).
* **Verification Command:**
  ```powershell
  cd work03-agent-workflow
  py -3.13 scripts/demo_offline.py
  # live with Postgres:
  .\make.ps1 boot
  .\scripts\reliability_demo.ps1
  ```

---

## Clean-Clone Reproducibility Matrix

Every project can be evaluated in two ways:
1. **Offline Mode (< 30 seconds):** Evaluates models, manifests, and mock scenarios without needing running Docker daemons.
2. **Full Live Cluster Mode:** Boots full stack in Docker Compose and executes live HTTP requests against microservices.

```powershell
# 1. Clone repository
git clone https://github.com/alexbohachev/portfolio-interview.git
cd portfolio-interview

# 2. Run offline validation across all 7 projects
.\scripts\repro_check.ps1

# 3. Run live Docker validation for Work 05 & Work 07
.\scripts\repro_check.ps1 -Docker
```

---

## All Eight Works Summary

| # | Project | Focus | Key Tech | Verification |
|---|---|---|---|---|
| **08** | Demand Forecasting | Multi-series forecasting, rolling backtesting, inventory risk | LightGBM, FastAPI, Pydantic, Pandas | `.\make.ps1 all` · [`REPORT.md`](work08-demand-forecasting/REPORT.md) |
| **07** | Distributed AI Platform | Enterprise microservices, N+1 fix, observability | Java 21, Python, Kafka, Elasticsearch, Jaeger | `.\make.ps1 smoke; py scripts/benchmark_latency.py` |
| **05** | DocGuard Gateway | Multi-tenant security, pre-LLM ACL, degraded mode | Java 21, FastAPI, Docker Compose | `.\scripts\reliability_demo.ps1` |
| **01** | Bank Marketing | ML classification, leakage guard, cost optimization | LightGBM, scikit-learn, Python 3.13 | `.\scripts\demo_offline.py` |
| **04** | ML Serving | Production serving, schema validation, drift guard | FastAPI, scikit-learn, joblib | `python -m work04 all` |
| **02** | RAG Citations | Hybrid RRF, citation accuracy, unanswerable gate | SentenceTransformers, BM25, NumPy | `.\make.ps1 all` |
| **03** | Agent Workflow | Idempotent workflow, Outbox, crash recovery | Java 21, Spring Boot, PostgreSQL, Docker | `.\scripts\reliability_demo.ps1` |
| **06** | Verse RAG | Semantic vector retrieval, SQLite metadata | FAISS, SentenceTransformers, SQLite | `pytest tests/` |
