# Інженерне портфоліо — AI Systems & Applied Machine Learning (8 робіт)

[![CI: Clean-Clone Reproducibility](https://github.com/alexbohachev/portfolio-interview/actions/workflows/repro.yml/badge.svg)](https://github.com/alexbohachev/portfolio-interview/actions/workflows/repro.yml)
[![All GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI_Runs-blue)](https://github.com/alexbohachev/portfolio-interview/actions)
[![Demo Video (60s MP4)](https://img.shields.io/badge/Demo_Video-60s_MP4_Walkthrough-blueviolet)](https://github.com/alexbohachev/portfolio-interview/blob/main/assets/work07_demo_walkthrough.mp4)
[![Demo Script (5-7 min)](https://img.shields.io/badge/Demo_Script-5--7_min_Walkthrough-purple)](https://github.com/alexbohachev/portfolio-interview/blob/main/work07-ai-platform/DEMO_SCRIPT_5MIN.md)
[![Live Demo Runner](https://img.shields.io/badge/Live_Demo-scripts%2Flive__interview.ps1-orange)](scripts/live_interview.ps1)

Відтворюване інженерне монорепозиторій із **8 проєктів та емпіричних бенчмарків**, що поєднує два напрями:
* **Розподілені AI-системи:** мікросервісна RAG-платформа (Java 21, Python 3.13, Docker, Kafka, Elasticsearch, Jaeger), відтворення антипатерну N+1, Pre-LLM Zero-Trust шлюз доступу до документів, Transactional Outbox і відновлення з checkpoint.
* **Прикладне машинне навчання та MLOps:** суворий часовий бектестинг на реальних даних UCI без витоку (leakage guard), прогнозування попиту на багатьох рядах з конформним калібруванням (синтетична симуляція + реальний датасет Capital Bikeshare) та сервінг моделей на FastAPI з контролем дрейфу ознак.

> **Англомовний огляд:** [`README.en.md`](README.en.md) · **Інструкція відтворення:** [`REPRO.md`](REPRO.md) · **Підготовка до співбесіди:** [`INTERVIEW_PREP.md`](INTERVIEW_PREP.md) · **Розбір N+1 кейсу:** [`CASE_N1_PERF.md`](work07-ai-platform/CASE_N1_PERF.md) · **Сценарій живого демо:** [`DEMO_SCRIPT_5MIN.md`](work07-ai-platform/DEMO_SCRIPT_5MIN.md) · **Автономний лонгрід:** [`STANDALONE_PORTFOLIO.md`](STANDALONE_PORTFOLIO.md)

```bash
# Швидка перевірка всіх 8 робіт (Linux / macOS / Windows):
python -m pytest work01-bank-marketing/tests work04-ml-serving/tests work08-demand-forecasting/tests
# Або через PowerShell:
.\scripts\repro_check.ps1
```

---

## Два головні інженерні треки

### 1. Трек AI Platform & Distributed RAG
* **Work 07 (Флагман):** Відтворення та усунення антипатерну N+1 викликів Java → Python RAG API. Підтверджено двома незалежними прогонами на локальному стенді Docker Compose (n=25):
  * **Базовий прогін (`6efad68`):** p95 знизився з **197.0 мс до 53.3 мс** (p50: 172.6 → 34.0 мс, прискорення 5.08×).
  * **Прогін із чистого клону (`45d550c`):** p95 знизився з **195.7 мс до 46.7 мс** (p50: 171.6 → 33.9 мс, прискорення 5.06× на p50, 4.19× на p95).
  * **Комічені сирі артефакти:** масиви вимірювань [`work07-ai-platform/manifests/latency_raw_samples.json`](work07-ai-platform/manifests/latency_raw_samples.json) та зведення [`work07-ai-platform/manifests/latency_before_after.json`](work07-ai-platform/manifests/latency_before_after.json).
  * **Оцінка пошуку на 8 складних запитах (`eval-hard`):** обидва методи (BM25 та Hybrid RRF) показали Recall@5 = 0.125 (1 з 8) і провалили 6 з 8 запитів (MRR@5: 0.063 у BM25 проти 0.031 у Hybrid). Висновок: bi-encoder без донавчання групує документи за широкими темами, але не розрізняє близькі термінологічні відтінки; наступний архітектурний крок — 2-й етап Cross-Encoder re-ranker. Комічені результати: [`work07-ai-platform/manifests/eval_per_query.json`](work07-ai-platform/manifests/eval_per_query.json).
  * Трейси перевірені в Jaeger (`http://localhost:16687`). Деталі: [`CASE_N1_PERF.md`](work07-ai-platform/CASE_N1_PERF.md).
* **Work 05 (DocGuard):** Pre-LLM Zero-Trust ACL шлюз. Перевірена ізоляція двох тенантів на 8 автоматизованих атакових сценаріях у CI, фіксація prompt injection в аудиторському лозі, автоматичний degraded mode (`degraded: true`) при відмові retrieval-сервісу.
* **Work 02 (RAG із цитатами):** Гібридний пошук (BM25 + Dense RRF), поріг відсікання галюцинацій (retrieval gate `0.0313`) та екстрактивна верифікація цитат (35/35).

### 2. Трек Applied Machine Learning & MLOps
* **Work 08 (Demand Forecasting):** Бектестинг прогнозування попиту на 4 сезонах ($H=14$ днів) за двома бенчмарками:
  1. *Синтетична агросимуляція (20 рядів):* LightGBM знижує WAPE з 13.20% до 7.83% (-41% помилки), оптимізація Newsvendor ($\tau^* = 83.33\%$) скорочує модельовані витрати на запаси на 43%, а CQR забезпечує спостережуване покриття $\ge 80.0\%$ (середнє 84.11% проти 75.90% у сирої моделі).
  2. *Реальні дані Capital Bikeshare (2011–2012):* простий сезонний бейзлайн переміг LightGBM (WAPE 35.42% проти 37.74%; витрати 33,576 проти 51,630 у.о.) — **і для продакшну обрано сезонний бейзлайн** за принципом бритви Оккама (менша похибка, нульові витрати на навчання та моніторинг дрейфу). CQR підняло покриття з 26.79% до 75.89%.
  * Деталі: [`work08-demand-forecasting/REPORT.md`](work08-demand-forecasting/REPORT.md).
* **Work 01 (ML на реальних даних):** UCI Bank Marketing без `duration` (leakage guard). Часовий сплит, облік сильного covariate shift (train 5.8% → test 39.3%), bootstrap 95% CI macro-F1 (`[-0.0085, 0.0089]`), що доводить чесний результат: нейромережа не перевершила збалансований лінійний бейзлайн на табличних даних. Аналіз помилок за 5 сегментами.
* **Work 04 (Production ML Serving):** Сервінг моделі на FastAPI (`/v1/predict`, `/v1/drift`). Data contract (`event_time` / `available_at`), поріг за бізнес-матрицею витрат, моніторинг вхідного дрейфу ознак через z-score.

---

## Роботи: перевірені можливості та чесні межі (Scope)

| № | Каталог | Що перевірено й доведено | Чесні операційні межі (Scope) | Статус |
|---|---|---|---|---|
| **08** | [`work08-demand-forecasting/`](work08-demand-forecasting/) | Прогнозування попиту на 20 рядах: LightGBM знижує WAPE на 40.7% проти Seasonal Naive на синтетиці; на реальних даних Bikeshare обрано бейзлайн (35.4% vs 37.7%); Newsvendor скорочує змодельовані втрати; CQR-калібрування. | Калібрована симуляція + реальний бенчмарк Bikeshare; операційний контракт горизонту $H=14$ днів. | **tag** `work08-v1.0` |
| **07** | [`work07-ai-platform/`](work07-ai-platform/) | Відтворення та усунення антипатерну N+1 (прискорення 5.1× на p50, 4.2× на p95); порівняння BM25 vs Hybrid на парафразах (Recall@5 = 0.125); Jaeger OTel трейси. | Локальний кластер Docker Compose; не гео-розподілений Kubernetes. | **tag** `work07-v1.0` |
| **05** | [`work05-docguard/`](work05-docguard/) | Zero-Trust Pre-LLM ACL шлюз: ізоляція тенантів на 8 автоматизованих атакових тестах у CI, audit log ін'єкцій, degraded fallback. | In-memory кеш ACL із REST-інвалідацією; не зовнішній провайдер посвідчень (Keycloak/Ory). | **tag** `work05-v1.0` |
| **01** | [`work01-bank-marketing/`](work01-bank-marketing/) | Усунення target leakage (`duration`), часовий backtesting, калібрування ймовірностей, bootstrap 95% CI на даних UCI. | Табличний датасет UCI; temperature scaling не усуває covariate shift повністю без domain adaptation. | **tag** `work01-v1.0` |
| **04** | [`work04-ml-serving/`](work04-ml-serving/) | Data contract (`event_time` vs `available_at`), поріг за матрицею витрат, живий моніторинг z-score дрейфу в FastAPI. | Перевірено на потокових батчах; у великому ентерпрайзі потребує коннектора до Feature Store. | **tag** `work04-v1.0` |
| **02** | [`work02-rag-citations/`](work02-rag-citations/) | Гібридний пошук RRF, калібрований refusal gate (`0.0313`), екстрактивна верифікація цитат без галюцинацій (35/35). | Корпус 200 документів; для щільних кластерів обґрунтовано тестування 2-го етапу Cross-Encoder re-ranker. | **tag** `work02-v1.0` |
| **03** | [`work03-agent-workflow/`](work03-agent-workflow/) | 3-кроковий ідемпотентний оркестратор, Transactional Outbox, 409 Conflict при зміні payload, відновлення з checkpoint (30/30 тестів). | Транзакційна межа Spring Boot + PostgreSQL на одному вузлі; не розподілений консенсус Raft/Paxos. | **tag** `work03-v1.0` |
| **06** | [`work06-bible-rag/`](work06-bible-rag/) | Семантичний пошук через векторний індекс FAISS, метадані в SQLite, автономний UI. | Класичний однопроцесний векторний індекс для автономного пошуку. | **tag** `work06-v1.0` |

---

## Швидкий запуск офлайн-демо

```bash
# Запуск офлайн-демо будь-якої роботи (< 10 секунд):
cd work08-demand-forecasting && python scripts/demo_offline.py
cd ../work07-ai-platform && python scripts/demo_offline.py
cd ../work05-docguard && python scripts/demo_offline.py
cd ../work01-bank-marketing && python scripts/demo_offline.py
```
