# Senior AI Backend Engineer — Portfolio Teardown

Production-grade monorepo of **7 end-to-end engineering projects** demonstrating distributed systems, AI/RAG infrastructure, performance engineering, and enterprise resilience.

> **Ukrainian documentation:** [`README.md`](README.md) · **Repro guide:** [`REPRO.md`](REPRO.md) · **Interview prep:** [`INTERVIEW_PREP.md`](INTERVIEW_PREP.md) · **N+1 case study:** [`CASE_N1_PERF.md`](work07-ai-platform/CASE_N1_PERF.md)

---

## 2-Minute Recruiter Summary

| Dimension | Proof in Monorepo | Impact |
|---|---|---|
| **Performance & Latency** | Work 07: Fixed N+1 microservice pattern Java → Python RAG API | **p95 reduced from 195.7 ms → 46.7 ms (4.19× speedup, p50 5.06×)** |
| **Enterprise AI Security** | Work 05: DocGuard zero-trust pre-LLM gateway (Java + FastAPI) | **100% tenant isolation across 8 security vectors, zero cross-tenant leak** |
| **Distributed Resilience** | Work 03: Fault-tolerant workflow engine (Transactional Outbox + Checkpoint) | **30/30 crash scenarios recovered without duplicate external effects** |
| **Search & Retrieval** | Work 02 & 07: Hybrid RRF search (Elasticsearch BM25 + dense kNN) | **1.0 Recall@5 on domain corpus; citation grounding & hallucination gate** |
| **Stack Competence** | Java 21 (Spring Boot 3, RestClient), Python 3.13 (FastAPI, PyTorch/SentenceTransformers), Docker Compose, Kafka, Elasticsearch, Jaeger, OpenTelemetry | **Single clone runs full offline suite + live Docker clusters** |

---

## 10-Minute Engineering Deep Dive: Three Flagship Cases

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

### 3. Work 03 — Agent Workflow: Crash Recovery & Transactional Outbox

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
