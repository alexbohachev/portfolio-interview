# Портфоліо — Senior AI/ML Engineer (7 робіт)

[![CI: Clean-Clone Reproducibility (Run #44543672145 Passed)](https://img.shields.io/badge/CI_Run_44543672145-Passed-brightgreen)](https://github.com/alexbohachev/portfolio-interview/actions/runs/44543672145)
[![All GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI_Runs-blue)](https://github.com/alexbohachev/portfolio-interview/actions)
[![Demo Walkthrough (5-7 min)](https://img.shields.io/badge/Demo_Recording-5--7_min_Walkthrough-purple)](work07-ai-platform/DEMO_SCRIPT_5MIN.md#quick-visual-summary-for-recruiters)
[![Live Demo Runner](https://img.shields.io/badge/Live_Demo-scripts%2Flive__interview.ps1-orange)](scripts/live_interview.ps1)

Monorepo для позиції **Senior AI/ML Engineer**: поєднання розподілених AI-платформ (Java 21, Python 3.13, RAG, OpenTelemetry) та класичного машинного навчання на реальних даних (часовий backtesting, MLOps, serving, drift).

**Документація:** [`INTERVIEW_PREP.md`](INTERVIEW_PREP.md) · [`PORTFOLIO.md`](PORTFOLIO.md) · **EN** [`README.en.md`](README.en.md) · [`REPRO.md`](REPRO.md) · [Автономний огляд (без репо)](STANDALONE_PORTFOLIO.md)

```powershell
.\scripts\repro_check.ps1
.\scripts\live_interview.ps1 work07   # smoke + bench + demo
```

## Два головні інженерні треки

### 1. Трек AI Platform & Distributed RAG (Головні кейси)
* **Work 07 (Флагман):** Усунення N+1 патерну викликів Java → Python RAG API. Підтверджено двома незалежними прогонами на локальному стенді Docker Compose (Windows 11, n=25):
  * **Базовий прогін (2026-11-18, `6efad68`):** p95 знизився з **197.0 мс до 53.3 мс** (p50: 172.6 → 34.0 мс, прискорення 5.08×).
  * **Прогін із чистого клону (2026-11-19, `45d550c`):** p95 знизився з **195.7 мс до 46.7 мс** (p50: 171.6 → 33.9 мс, прискорення 5.06× на p50, 4.19× на p95).
  * **Комічені сирі артефакти:** сирі масиви замірів латентності по 25 викликів [`manifests/latency_raw_samples.json`](work07-ai-platform/manifests/latency_raw_samples.json) та зведення [`manifests/latency_before_after.json`](work07-ai-platform/manifests/latency_before_after.json).
  * **Порівняння BM25 vs Hybrid на складних запитах (`eval-hard`):** на парафразах `hard_007` гібридний RRF виграв (+1 hit) завдяки семантичному узагальненню; на `hard_006` (дози NPK) BM25 виграв (+1 hit) завдяки точним формулам; на щільних кластерах обґрунтовано тестування 2-го етапу — Cross-Encoder re-ranker. Повний JSON результатів по кожному запиту: [`manifests/eval_per_query.json`](work07-ai-platform/manifests/eval_per_query.json).
  * Трейси перевірені в Jaeger (`http://localhost:16687`). Деталі: [`CASE_N1_PERF.md`](work07-ai-platform/CASE_N1_PERF.md) та сценарій демо: [`DEMO_SCRIPT_5MIN.md`](work07-ai-platform/DEMO_SCRIPT_5MIN.md).
* **Work 05 (DocGuard):** Pre-LLM Zero-Trust ACL шлюз. 100% ізоляція двох тенантів на 8 безпекових векторах, фіксація prompt injection у незмінному аудиторському лозі, автоматичний degraded mode (`degraded: true`) при зупинці retrieval-сервісу (`scripts/reliability_demo.ps1`).
* **Work 02 (RAG із цитатами):** Гібридний пошук (BM25 + Dense RRF), поріг відсікання галюцинацій (retrieval gate `0.0313`) та екстрактивна верифікація цитат (35/35).

### 2. Трек Applied Machine Learning & MLOps
* **Work 01 (ML на реальних даних):** UCI Bank Marketing без `duration` (leakage guard). Суворий часовий сплит без заглядання в майбутнє, чесний облік сильного covariate shift (train 5.8% → val 11.5% → test 39.3% yes), bootstrap 95% довірчий інтервал різниці macro-F1 (`[-0.0085, 0.0089]`), що доводить чесний негативний результат MLP vs збалансованого лінійного baseline, поглиблений аналіз помилок по 5 сегментах.
* **Work 04 (Production ML Serving):** Сервінг моделі на FastAPI (`/v1/predict`, `/v1/drift`). Data contract із часовими мітками `event_time` / `available_at`, оптимізація порогу за матрицею бізнес-вартості ($C_{FN}$ vs $C_{FP}$ vs $C_{review}$), моніторинг вхідного дрейфу ознак через z-score.

---

## Роботи: перевірені можливості та чесні межі (Scope)

| № | Каталог | Що перевірено й доведено | Чесні операційні межі (Scope) | Статус |
|---|---|---|---|---|
| **07** | [`work07-ai-platform/`](work07-ai-platform/) | Усунення N+1 латентності Java→Python (speedup ~5.1× на p50, ~4.2× на p95); порівняння BM25 vs Hybrid на парафразах; Jaeger OTel трейси. | Локальний кластер Docker Compose; не гео-розподілений багаторегіональний Kubernetes. | **tag** `work07-v1.0` |
| **05** | [`work05-docguard/`](work05-docguard/) | Zero-Trust Pre-LLM ACL шлюз: 100% ізоляція 2 тенантів на 8 векторах, audit log ін'єкцій, degraded fallback при відмові Python. | In-memory кеш ACL із REST-інвалідацією; не зовнішній провайдер посвідчень (Keycloak/Ory). | **tag** `work05-v1.0` |
| **01** | [`work01-bank-marketing/`](work01-bank-marketing/) | Усунення target leakage (`duration`), часовий backtesting, калібрування ймовірностей, bootstrap 95% CI на реальних даних UCI. | Табличний датасет UCI; temperature scaling не усуває covariate shift повністю без domain adaptation. | **tag** `work01-v1.0` |
| **04** | [`work04-ml-serving/`](work04-ml-serving/) | Data contract (`event_time` vs `available_at`), поріг за бізнес-матрицею витрат, живий моніторинг z-score дрейфу в FastAPI. | Перевірено на потокових батчах подій; у великому ентерпрайзі потребує коннектора до Feature Store. | **tag** `work04-v1.0` |
| **02** | [`work02-rag-citations/`](work02-rag-citations/) | Гібридний пошук RRF, калібрований refusal gate (`0.0313`), екстрактивна верифікація цитат без галюцинацій (35/35). | Корпус 200 агро-документів; для щільних термінологічних кластерів логічною гіпотезою для тестування є Cross-Encoder re-ranker. | **tag** `work02-v1.0` |
| **03** | [`work03-agent-workflow/`](work03-agent-workflow/) | 3-кроковий ідемпотентний оркестратор, Transactional Outbox, 409 Conflict при зміні payload, відновлення з checkpoint (30/30 fault-тестів). | Транзакційна межа Spring Boot + PostgreSQL на одному вузлі; не розподілений консенсус Raft/Paxos. | **tag** `work03-v1.0` |
| **06** | [`work06-bible-rag/`](work06-bible-rag/) | Семантичний пошук через векторний індекс FAISS, метадані в SQLite, Streamlit UI. | Класичний однопроцесний векторний індекс для автономного пошуку. | **tag** `work06-v1.0` |

## Запуск (приклад)

Windows:

```powershell
cd work06-bible-rag
py -3.13 -m pip install -r requirements.txt
.\make.ps1 all
```

## Стандарт

Усі роботи: одна команда повного циклу, baseline + candidate (де в ТЗ), незалежний test, `REPORT.md`, lock/manifest залежностей.