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

`scripts/benchmark_latency.py` (n=25):

| Профіль | p50 | p95 |
|---------|-----|-----|
| **slow** (N+1) | 172.6 ms | 197.0 ms |
| **fast** (1× hybrid) | 34.0 ms | 53.3 ms |

**speedup p50 ≈ 5.1×** — `artifacts/latency_before_after.json`, деталі `PERFORMANCE.md`.

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

`DEMO.md`, `scripts/demo.ps1` — запис відео 5–7 хв для співбесіди.