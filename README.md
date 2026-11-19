# Портфоліо — Senior AI/ML Engineer (7 робіт)

Monorepo для позиції **Senior AI/ML Engineer**: поєднання розподілених AI-платформ (Java 21, Python 3.13, RAG, OpenTelemetry) та класичного машинного навчання на реальних даних (часовий backtesting, MLOps, serving, drift).

**Документація:** [`INTERVIEW_PREP.md`](INTERVIEW_PREP.md) · [`PORTFOLIO.md`](PORTFOLIO.md) · **EN** [`README.en.md`](README.en.md) · [`REPRO.md`](REPRO.md) · [Автономний огляд (без репо)](STANDALONE_PORTFOLIO.md)

```powershell
.\scripts\repro_check.ps1
.\scripts\live_interview.ps1 work07   # smoke + bench + demo
```

## Два головні інженерні треки

### 1. Трек AI Platform & Distributed RAG (Головні кейси)
* **Work 07 (Флагман):** Усунення N+1 патерну викликів Java → Python RAG API. Зниження **p95 з 195.7 мс до 46.7 мс (speedup ~4.2×)** підтверджено трейсами в Jaeger (`http://localhost:16687`). Деталі: [`CASE_N1_PERF.md`](work07-ai-platform/CASE_N1_PERF.md) та сценарій демо: [`DEMO_SCRIPT_5MIN.md`](work07-ai-platform/DEMO_SCRIPT_5MIN.md).
* **Work 05 (DocGuard):** Pre-LLM Zero-Trust ACL шлюз. Ізоляція тенантів, захист від prompt injection у логах, degraded mode при недоступності retrieval (`scripts/reliability_demo.ps1`).
* **Work 02 (RAG із цитатами):** Гібридний пошук (BM25 + Dense RRF), поріг відмови від галюцинацій (retrieval gate) та extractive citations.

### 2. Трек Applied Machine Learning & MLOps
* **Work 01 (ML на реальних даних):** UCI Bank Marketing без `duration` (leakage guard). Суворий часовий сплит без заглядання в майбутнє, облік сильного covariate shift (train 5.8% → test 39.3% yes), bootstrap довірчий інтервал різниці macro-F1, поглиблений аналіз помилок по сегментах.
* **Work 04 (Production ML Serving):** Сервінг моделі на FastAPI (`/v1/predict`, `/v1/drift`). Data contract із часовими мітками `event_time` / `available_at`, оптимізація порогу за матрицею бізнес-вартості (FP/FN/review), моніторинг вхідного дрейфу ознак через z-score.

---

## Роботи (усі зафіксовані тегами v1.0)

| № | Каталог | Фокус ролі | Статус |
|---|---------|------------|--------|
| **07** | [`work07-ai-platform/`](work07-ai-platform/) | AI Platform: Java 21 + Python, N+1 латентність, Kafka, ES, Jaeger | **tag** `work07-v1.0` |
| **05** | [`work05-docguard/`](work05-docguard/) | AI Security: Zero-Trust Pre-LLM ACL Gateway, Degraded fallback | **tag** `work05-v1.0` |
| **01** | [`work01-bank-marketing/`](work01-bank-marketing/) | Classical ML: часовий backtesting, covariate shift, leakage guard | **tag** `work01-v1.0` |
| **04** | [`work04-ml-serving/`](work04-ml-serving/) | MLOps / Serving: Data contracts (`available_at`), cost matrix, drift | **tag** `work04-v1.0` |
| **02** | [`work02-rag-citations/`](work02-rag-citations/) | RAG Science: Hybrid RRF, citation grounding, retrieval gate | **tag** `work02-v1.0` |
| **03** | [`work03-agent-workflow/`](work03-agent-workflow/) | Distributed Systems: Transactional Outbox, checkpoint recovery | **tag** `work03-v1.0` |
| **06** | [`work06-bible-rag/`](work06-bible-rag/) | Semantic Search: FAISS vector retrieval, SQLite, Streamlit UI | **tag** `work06-v1.0` |

## Запуск (приклад)

Windows:

```powershell
cd work06-bible-rag
py -3.13 -m pip install -r requirements.txt
.\make.ps1 all
```

## Стандарт

Усі роботи: одна команда повного циклу, baseline + candidate (де в ТЗ), незалежний test, `REPORT.md`, lock/manifest залежностей.