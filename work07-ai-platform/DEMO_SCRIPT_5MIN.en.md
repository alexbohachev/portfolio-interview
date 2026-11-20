[Українська](DEMO_SCRIPT_5MIN.md) | **English**

# 5–7 Minute Live Demo Script: Work 07 & N+1 Latency Elimination

This script is written for a live screen demonstration during a technical interview for a **Senior AI Backend Engineer** role, or for an asynchronous walk-through of how the N+1 anti-pattern was removed.

> **Artifact format:** 🎬 **Demo video (MP4):** [`assets/work07_demo_walkthrough.mp4`](../assets/work07_demo_walkthrough.mp4) (a video walk-through of the architecture, Jaeger traces and the benchmark with timings) and an interactive step-by-step walkthrough script. To run it live in a terminal use: `.\scripts\live_interview.ps1 work07`.

---

## ⚡ Quick overview for a recruiter / asynchronous viewing (2-minute summary)

If you do not have a Docker environment running, this section shows the exact visual flow of the demo:

```
[0:00 - 1:00] ARCHITECTURE:
Java 21 (Logistics/Farm/Scout) ──(REST/Kafka)──► Python 3.13 FastAPI (RAG API) ──► Elasticsearch 8.17 (BM25 + kNN)
                              └──(OpenTelemetry Agent)──► Jaeger UI (:16687)

[1:00 - 2:30] DIAGNOSING THE N+1 ANTI-PATTERN IN JAEGER:
HTTP POST /api/v1/equipment-requests (Profile: slow)
 │
 ├── span: token_1 ──► GET /v1/knowledge/search?q=бура (~28 ms)
 ├── span: token_2 ──► GET /v1/knowledge/search?q=іржа (~26 ms)
 ├── span: token_3 ──► GET /v1/knowledge/search?q=озимої (~31 ms)
 ├── span: token_4 ──► GET /v1/knowledge/search?q=пшениці (~29 ms)
 └── span: full_q  ──► GET /v1/knowledge/search?q=бура+іржа... (~38 ms)
     Total p95 = 231.5 ms (6 sequential network HTTP calls)

[2:30 - 3:45] ARCHITECTURAL FIX:
The loop over tokens in `EquipmentSearchService.java` was removed. A single `searchFast()` call was introduced.
The Python RAG API performs Reciprocal Rank Fusion (RRF) directly inside Elasticsearch.

[3:45 - 5:15] BENCHMARK RESULT:
HTTP POST /api/v1/equipment-requests (Profile: fast)
 └── single span ──► GET /v1/knowledge/search (hybrid Top-3)
     Total p95 = 46.9 ms (4.94× speedup at p95, 5.06× at p50)

[5:15 - 7:00] HONEST RETRIEVAL EVALUATION:
* hard_007 (disease risks across seasons): Hybrid won (+1 hit) thanks to semantic generalization.
* hard_006 (NPK doses): BM25 won (+1 hit) thanks to an exact match of the formula notation.
```

> **How to reproduce it live yourself:**  
> Run in a terminal: `.\scripts\live_interview.ps1 work07`. The script automatically brings up the cluster, runs the benchmark and shows the results.

---

## Preparation before starting (2 minutes before the call)

1. Start Docker Desktop.
2. Open a terminal in `work07-ai-platform`:
   ```powershell
   .\make.ps1 build; .\make.ps1 up
   ```
3. Open two browser tabs:
   * **Jaeger UI:** [http://localhost:16687](http://localhost:16687)
   * **RAG API Health:** [http://localhost:8090/health](http://localhost:8090/health) (`indexed_docs: 206`)
4. Open the code file in the editor:
   * `work07-ai-platform/services/logistics/src/main/java/ua/agrichain/logistics/service/EquipmentSearchService.java`

---

## Talk timing (5–7 minutes)

### [0:00 – 1:00] Context and system architecture
* **What to show on screen:** the architecture diagram in `README.en.md` or a terminal window with the running containers (`docker compose ps`).
* **What to say:**
  > "This is a distributed platform for an agricultural enterprise. The architecture is hybrid: three Java 21 microservices (Farm, Scout, Logistics) and an intelligent RAG service in Python 3.13 / FastAPI, connected through Kafka, Elasticsearch 8.17 and OpenTelemetry/Jaeger.
  > When a field technician creates an equipment request through the Logistics Service, the system must not just create a record, it has to find the fungicide application rule or norms using hybrid search (dense + BM25)."

---

### [1:00 – 2:30] How I found the problem (Jaeger & the N+1 anti-pattern)
* **What to show on screen:** Jaeger UI (`http://localhost:16687`), search for the `logistics` service. Open the trace of a request with the `slow` profile.
* **What to say:**
  > "During load testing of the `POST /api/v1/equipment-requests` endpoint we noticed a high p95 latency, almost 200 milliseconds on the local stand.
  > I opened distributed tracing in Jaeger. Look at this cascade: instead of a single call to the knowledge service, the Logistics service split the query string into separate tokens and called the Python RAG API sequentially for each token, plus one more call for the full phrase.
  > This is the classic distributed anti-pattern of **N+1 HTTP calls**. Every call adds network latency, JSON serialization and request-queue overhead."

---

### [2:30 – 3:45] What exactly was changed in the code (Java → Python)
* **What to show on screen:** `EquipmentSearchService.java` (compare the `searchSlow` and `searchFast` methods).
* **What to say:**
  > "I reworked the integration contract:
  > Instead of a loop over tokens we implemented a single batched hybrid call, `searchFast()`.
  > In the Python service we use Reciprocal Rank Fusion (RRF) directly in Elasticsearch: we combine kNN dense vectors (SentenceTransformers) and sparse BM25 search in one query.
  > We also added resilience policies: timeouts at the RestClient level, structured DTOs, and contract backward compatibility via HTTP headers."

---

### [3:45 – 5:15] Evidence and a live benchmark (a stable ~4–5× speedup)
* **What to show on screen:** run the benchmark in the terminal:
  ```powershell
  py -3.13 scripts/benchmark_latency.py
  ```
* **What to say:**
  > "Now I am running a standardized 25-iteration benchmark under identical local-stand conditions.
  > We recorded two independent runs: a baseline (p95: 197.0 → 53.3 ms) and a control run from a clean clone (p95: 231.5 → 46.9 ms, p50: 171.6 → 33.9 ms).
  > Both runs show the same result: **a 5.1× speedup at p50 and 4.9× at p95 (Run 2; Run 1: 3.7× with the old method)** (~80% reduction in response time).
  > All raw timings and timestamps are written to `artifacts/latency_raw_samples.json` together with the commit hash for audit."

---

### [5:15 – 6:15] Search quality validation (BM25 vs Hybrid on hard queries)
* **What to show on screen:** run or report of `make.ps1 eval-hard`:
  ```powershell
  .\make.ps1 eval-hard
  ```
* **What to say:**
  > "Speed must not degrade quality. On the simple synthetic set both BM25 and the hybrid have Recall@5 = 1.0. So we ran `eval-hard` on a sample of hard paraphrases and multi-hop questions.
  > The results give an honest picture:
  > On query `hard_007` (disease risks across seasons) the hybrid wins: the dense vectors understood the semantics, while BM25 did not find the exact words and missed the document.
  > On query `hard_006` (NPK doses) BM25 wins thanks to an exact match of numeric notation and formulas.
  > And for subtle differences within dense clusters, the logical hypothesis to test is a second stage: a Cross-Encoder re-ranker on the Top-20 candidates. That gives a balanced architecture without blind spots."

---

### [6:15 – 7:00] Takeaway for a Senior role
* **What to say:**
  > "This case shows my approach to Senior AI Backend work:
  > 1. Do not optimize at random; find bottlenecks through distributed telemetry (Jaeger / OpenTelemetry).
  > 2. Understand the internal interaction between JVM services and the Python AI runtime.
  > 3. Record results in reproducible metrics and tests that pass in CI from a clean clone."
