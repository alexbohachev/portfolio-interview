# Senior AI/ML Engineer — Portfolio Teardown

Production-grade monorepo of **7 end-to-end engineering projects** demonstrating dual-track mastery: **Distributed AI/RAG Infrastructure** (Java 21, Python 3.13, Docker, Kafka, OpenTelemetry) and **Applied Machine Learning / MLOps** (temporal backtesting, target leakage prevention, probability calibration, production serving, drift detection).

> **Ukrainian documentation:** [`README.md`](README.md) · **Repro guide:** [`REPRO.md`](REPRO.md) · **Interview prep:** [`INTERVIEW_PREP.md`](INTERVIEW_PREP.md) · **N+1 case study:** [`CASE_N1_PERF.md`](work07-ai-platform/CASE_N1_PERF.md) · **Live demo script:** [`DEMO_SCRIPT_5MIN.md`](work07-ai-platform/DEMO_SCRIPT_5MIN.md) · **Standalone guide:** [`STANDALONE_PORTFOLIO.md`](STANDALONE_PORTFOLIO.md)

---

## 2-Minute Recruiter Summary

| Dimension | Proof in Monorepo | Engineering Impact |
|---|---|---|
| **AI Systems & Performance** | Work 07: Eliminated N+1 microservice pattern Java → Python RAG API | **p95 reduced 195.7 ms → 46.7 ms (4.19× speedup, p50 5.06×)**; confirmed in Jaeger |
| **Enterprise AI Security** | Work 05: DocGuard zero-trust pre-LLM gateway (Java + FastAPI) | **100% tenant isolation across 8 security vectors, zero cross-tenant leak**, degraded fallback |
| **Applied ML & Temporal Backtesting** | Work 01: Real UCI data, temporal validation without lookahead bias | **Strict target leakage guard (`duration` removed), honest covariate shift handling (5.8%→39.3%)**, bootstrap CI |
| **Production ML Serving & Drift** | Work 04: Production serving on FastAPI with temporal data contracts | **`event_time` vs `available_at` contracts, business cost matrix thresholding, live feature drift alerts** |
| **Distributed Resilience** | Work 03: Fault-tolerant workflow engine (Transactional Outbox + Checkpoint) | **30/30 crash scenarios recovered without duplicate external side effects** |
| **Search & Retrieval Science** | Work 02 & 07: Hybrid RRF search (Elasticsearch BM25 + dense kNN) | **1.0 Recall@5 on domain corpus; hallucination gate threshold tuned on validation** |
| **Full Stack Competence** | Java 21 (Spring Boot 3, RestClient), Python 3.13 (FastAPI, PyTorch/SentenceTransformers), Docker, Kafka, Elasticsearch, Jaeger | **Single clean clone runs 100% reproducible offline suite + live Docker clusters** |

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
* **Empirical Verification (Local Docker Bench, 25 samples):**
  * `slow` profile (N+1): **p50 = 171.6 ms**, **p95 = 195.7 ms**, mean = 179.2 ms
  * `fast` profile (batch): **p50 = 33.9 ms**, **p95 = 46.7 ms**, mean = 37.9 ms
  * **Net Speedup:** **5.06× at p50**, **4.19× at p95**
* **Verification Command:**
  ```powershell
  cd work07-ai-platform
  .\make.ps1 build; .\make.ps1 up
  py -3.13 scripts/benchmark_latency.py
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

* **The Problem:** Non-deterministic external tool calls (API effects, machinery commands, logistics dispatch) can execute twice if network fails after the side effect but before the workflow commits state.
* **The Architecture:**
  * **Idempotency Guard:** `idempotency_key` + SHA-256 payload hash uniquely identifies intents. A duplicate request with matching payload returns the cached result; an altered payload triggers `409 Conflict`.
  * **Transactional Outbox:** External intents are stored in PostgreSQL within the same ACID transaction as the workflow state checkpoint.
  * **Recovery Loop:** On restart after a sudden power loss or process kill, `WorkflowRecovery` inspects pending outbox entries, verifies external stub effects, and resumes from the exact checkpoint without re-running external side effects.
  * **Matrix Tests:** 30 automated fault scenarios (`idempotency: 8`, `checkpoint_recovery: 4`, `validation_400: 7`, `outbox: 3`, `conflict_409: 4`, `domain: 4`).
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

## All Seven Works Summary

| # | Project | Focus | Key Tech | Verification |
|---|---|---|---|---|
| **01** | Bank Marketing | ML classification, leakage guard, cost optimization | LightGBM, scikit-learn, Python 3.13 | `.\scripts\demo_offline.py` |
| **02** | RAG Citations | Hybrid RRF, citation accuracy, unanswerable gate | SentenceTransformers, BM25, NumPy | `.\make.ps1 all` |
| **03** | Agent Workflow | Idempotent workflow, Outbox, crash recovery | Java 21, Spring Boot, PostgreSQL, Docker | `.\scripts\reliability_demo.ps1` |
| **04** | ML Serving | Production serving, schema validation, drift guard | FastAPI, scikit-learn, joblib | `python -m work04 all` |
| **05** | DocGuard Gateway | Multi-tenant security, pre-LLM ACL, degraded mode | Java 21, FastAPI, Docker Compose | `.\scripts\reliability_demo.ps1` |
| **06** | Verse RAG | Semantic vector retrieval, SQLite metadata | FAISS, SentenceTransformers, SQLite | `pytest tests/` |
| **07** | Distributed AI Platform | Enterprise microservices, N+1 fix, observability | Java 21, Python, Kafka, Elasticsearch, Jaeger | `.\make.ps1 smoke; py scripts/benchmark_latency.py` |
