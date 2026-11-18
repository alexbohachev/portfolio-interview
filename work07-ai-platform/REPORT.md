# Звіт — робота 7 (MVP стенд)

## Статус

Compose піднімає **8 контейнерів**; smoke: farm → scout → logistics → rag-api → Elasticsearch.

## Архітектура

```text
logistics (Java) --REST--> rag-api (FastAPI) --> Elasticsearch
worker (Python) <--Kafka-- redpanda
```

## Smoke (scripts/smoke_test.py)

- `GET /api/v1/fields`
- `POST /api/v1/observations`
- `POST /api/v1/equipment-requests` + knowledgeHits

## Обмеження MVP

- Один seed-документ у ES; без evaluation golden
- LLM вимкнено
- Postgres поки без схем домену

## Наступний крок

Hybrid dense+kNN, seed корпус із work02, GitLab CI, один оцінений LLM.