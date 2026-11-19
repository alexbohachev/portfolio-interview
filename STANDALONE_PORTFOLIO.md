# Senior AI/ML Engineer — Portfolio Teardown & Engineering Evidence

> **Author:** Alex Bohachev  
> **Target Role:** Senior AI/ML Engineer / Senior AI Platform Engineer  
> **Core Focus:** Distributed AI & RAG Infrastructure · Applied Machine Learning & MLOps · High-Performance Backend Systems  
> **Repository:** Monorepo across Java 21, Python 3.13, Docker, Elasticsearch, Kafka, OpenTelemetry/Jaeger  

---

## 1. Executive Summary (The 2-Minute Recruiter Overview)

This portfolio documents **7 production-grade engineering projects** solving concrete challenges at the intersection of AI infrastructure, classical machine learning, and distributed reliability.

| Core Competency | Demonstrated In | Measurable Outcome & Engineering Evidence |
|---|---|---|
| **Distributed Performance & Latency** | **Work 07 (AI Platform)** | Eliminated **N+1 HTTP calls** from Java microservices to Python RAG API. Reduced **p95 latency from 195.7 ms → 46.7 ms (4.19× speedup, p50 5.06×)**, verified via OpenTelemetry/Jaeger distributed tracing. |
| **Enterprise AI Security & Governance** | **Work 05 (DocGuard)** | Zero-Trust Pre-LLM Security Gateway. Enforces multi-tenant principal ACL filtering **before** documents reach LLM or vector search. **100% tenant isolation across 8 security scenarios**, verbatim prompt injection audit logging, automated degraded mode. |
| **Applied ML & Temporal Backtesting** | **Work 01 (Bank Marketing)** | Production-grade tabular ML on real UCI data. Strict **target leakage elimination** (removed post-call `duration`), chronological temporal backtesting, honest handling of severe covariate shift (5.8% → 39.3%), bootstrap confidence intervals. |
| **Production ML Serving & MLOps** | **Work 04 (Risk Serving)** | Low-latency FastAPI model serving. Explicit data contracts separating `event_time` from `available_at`, **business cost matrix optimization** (FP/FN/review cost), calibrated LightGBM, and live feature drift detection via z-score monitoring. |
| **Search & Retrieval Science** | **Work 02 (RAG Citations)** | Hybrid search combining **dense kNN embeddings and BM25 via Reciprocal Rank Fusion (RRF)**. Calibrated refusal threshold gate preventing hallucinations on unanswerable queries, with strict extractive citation verification. |
| **Distributed Systems Resilience** | **Work 03 (Agent Workflow)** | Deterministic 3-step orchestrator with **Transactional Outbox and Checkpoint recovery**. Survives random process crashes and network partitions without duplicate external side effects (**30/30 fault scenarios passing**). |

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

#### Quantitative Benchmarking (Local Docker Stand, 25 samples each):
* **`slow` profile (N+1 iterative):** p50 = 171.6 ms | **p95 = 195.7 ms** | mean = 179.2 ms
* **`fast` profile (batch hybrid):** p50 = 33.9 ms | **p95 = 46.7 ms** | mean = 37.9 ms
* **Net Performance Gain:** **5.06× speedup at p50, 4.19× speedup at p95** (~76% latency reduction).

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
In distributed workflow systems, network partitions or process crashes occurring immediately after invoking an external third-party API (payment gateway, equipment dispatch) can cause repeated duplicate execution upon retry.

#### The Architecture
* **Idempotency Guard:** Every workflow execution requires an `idempotency_key` and SHA-256 command hash. Retrying with identical parameters safely returns the cached result; retrying with altered parameters returns `409 Conflict`.
* **Transactional Outbox:** Intent to call external services is written to PostgreSQL inside the same atomic database transaction as the workflow state checkpoint.
* **Crash Recovery Loop:** If the node crashes after an external side-effect is recorded, `WorkflowRecovery` verifies existing effects on startup, completes the pending checkpoint, and marks the workflow `COMPLETED` without re-issuing duplicate external calls.
* **Fault Injection Matrix:** 30 automated fault injection scenarios verified in CI (`idempotency: 8`, `checkpoint_recovery: 4`, `validation_400: 7`, `outbox: 3`, `conflict_409: 4`, `domain: 4`).

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
