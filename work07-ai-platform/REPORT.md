[**Українська**](REPORT.md) | [English](REPORT.en.md)

# Звіт — робота 7 (AI-платформа Compose MVP)

**Дата фінального прогону:** 2026-11-18  
**Стенд:** локальний Docker Compose (Windows), корпус work02 **200** md.  
**Manifest:** `manifests/test_manifest.json` (`config_hash` = `87dbd806dbe8a914`).

## Архітектура

| Шар | Компоненти |
|-----|------------|
| Java | farm, scout, logistics → REST + Kafka |
| Python | rag-api (hybrid, Q&A), worker (index, recommendations, DLQ) |
| Дані | Elasticsearch, Redpanda, Postgres, Jaeger (`:16687`) |

## Smoke

`py -3.13 scripts/smoke_test.py` — **OK** (indexed=200, hybrid, Q&A via logistics, Kafka farm/scout, slow profile).

## Retrieval (golden test, n=50)

| Метрика | BM25 | Hybrid |
|---------|------|--------|
| Recall@5 | **1.00** | **1.00** |
| MRR@5 | **1.00** | **1.00** |

Джерело: `data/golden/test.json` (50 нових питань work07). Артефакт: `artifacts/eval_results.json`.

## Рекомендації (test, n=20)

| Метрика | Значення |
|---------|----------|
| Hit@3 | **0.65** |
| precision@3 | **0.23** |
| citation_support_rate | **0.23** |

Евристичний matcher + довідник 30 дій; покращення — ML/LLM candidate. Артефакт: `artifacts/recommendation_eval.json`.

## Продуктивність logistics → rag-api

`scripts/benchmark_latency.py` (n=25 на профіль, `POST /api/v1/equipment-requests`):

| Прогін | Дата й Git SHA | Умови | Профіль slow (N+1) | Профіль fast (1× Hybrid) | Speedup (p50 / p95) | Артефакти |
|---|---|---|---|---|---|---|
| **Run 1** (Baseline) | 2026-11-18 (`6efad68`) | Локальний Docker Compose, Win11 | p50: **172.6 ms**<br>p95: **197.0 ms** | p50: **34.0 ms**<br>p95: **53.3 ms** | **5.08×** (p50)<br>**3.70×** (p95) | `manifests/latency_snapshot.json` |
| **Run 2** (Clean-clone) | 2026-11-19 (`45d550c`) | Повний рестарт контейнерів, Win11 | p50: **171.6 ms**<br>p95: **231.5 ms** | p50: **33.9 ms**<br>p95: **46.9 ms** | **5.06×** (p50)<br>**4.94×** (p95) | `manifests/latency_before_after.json`<br>`manifests/latency_raw_samples.json` |

Обидва незалежні прогони підтверджують стабільне скорочення затримки в **~5.1× на p50** та **~4–5× на p95** (Run 1: 3.70× старим методом; Run 2: 4.94×; ~80% зниження latency у Run 2) без погіршення результатів пошуку. Детальний аналіз: `CASE_N1_PERF.md`. Примітка щодо методу: перцентилі Run 2 перераховано з лінійною інтерполяцією (стандарт numpy) із закомічених сирих вибірок (`manifests/latency_raw_samples.json`). Перші цифри p95 (195.7 / 46.7 мс) рахувалися floor-індексом (23-тє з 25 значень, близько p92) і замінені. При n=25 p95 визначають два найповільніші запити, тож це орієнтовна оцінка; Run 1 лишено як було зафіксовано (старий метод, сирих вибірок немає).

## Retrieval на складних запитах (`eval-hard`, n=8 оцінених)

`.\make.ps1 eval-hard` (або `py -3.13 scripts/eval_retrieval.py --golden-file data/golden/hard_retrieval.json --per-query --doc-id-prefix agri_`):

| Запит | Цільовий doc_id | BM25 Hit@5 | Hybrid Hit@5 | Підсумок порівняння |
|---|---|:---:|:---:|---|
| `hard_007`: «Порівняти ризики хвороб пшениці в різних сезонах» | `agri_015_wheat_disease_14` | ❌ (Miss) | **✅ (Rank 4)** | **Hybrid виграв (+1)**: семантичне узагальнення зв'язку хвороб та сезонів |
| `hard_006`: «Дози азоту фосфору в NPK для поля» | `agri_062_npk_fertilizer_1` | **✅ (Rank 2)** | ❌ (Miss) | **BM25 виграв (+1)**: точний збіг термінів і пропорцій формули |
| `hard_001`–`005`, `010`: парафрази та синоніми | Різні (агро-кластери) | ❌ | ❌ | **Кластерний паритет**: знайдено релевантні кластери, гіпотеза для тесту — Cross-Encoder |
| `hard_008`, `hard_009`: нерелевантні (поза доменом) | Відсутні | Відфільтровано | Відфільтровано | **Коректна відмова (Gate)**: нуль галюцинацій |

Артефакти: `manifests/hard_eval_snapshot.json` та `artifacts/eval_per_query.json`.

## Інше (MVP)

- Resilience4j на logistics; read timeout 120s.
- OpenAPI: `openapi/rag-api.openapi.json`.
- OTel: Java + FastAPI → Jaeger **http://localhost:16687**.
- OpenAI: `.\make.ps1 eval-llm` опційно (ключ не в репозиторії).

## Обмеження (чесно)

- Recall 1.0 на **синтетичному** корпусі work02 (очікувано завищено vs відкриті дані).
- Рекомендації: rule-based, не Hit@3 з ТЗ-еталоном 40 розмічених спостережень у проді.
- Згенерований Java OpenAPI-клієнт, k6, другий embeddings-індекс — після MVP.

## Прийняття (work07-v1.0)

```powershell
cd c:\Portfolio\work07-ai-platform
.\make.ps1 all          # або up + smoke після jar
.\make.ps1 finalize    # smoke + eval + bench + lock
```

Після коміту: `git tag -a work07-v1.0 -m "Робота 7: Compose AI platform MVP"`.

## Демо

* 🎬 **Відеозапис демо (MP4 Walkthrough):** [`assets/work07_demo_walkthrough.mp4`](../assets/work07_demo_walkthrough.mp4) — відеопрезентація архітектури, трейсів у Jaeger та виміряних таймінгів p50/p95.
* **Покроковий сценарій:** [`DEMO_SCRIPT_5MIN.md`](DEMO_SCRIPT_5MIN.md), `DEMO.md`, `scripts/demo.ps1`.
* **Живий запуск наживо в терміналі:** `.\scripts\live_interview.ps1 work07`.