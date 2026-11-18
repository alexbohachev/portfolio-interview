# Звіт — робота 7 (ітерація hybrid + Q&A)

## Зроблено

- Індексація **200** md з work02 у Elasticsearch (`dense_vector` 384 + text).
- Пошук: `mode=bm25|hybrid` (RRF).
- Q&A: extractive + цитати; **OpenAI** якщо `OPENAI_API_KEY`.
- Logistics проксіє `knowledge/qa` і `equipment-requests` (hybrid search).

## Smoke (`scripts/smoke_test.py`)

- health `indexed_docs`
- hybrid search non-empty
- qa not refused + citations
- logistics equipment-requests

## Демо

`scripts/demo.ps1` + `DEMO.md` (5–7 хв).

## Наступний крок ТЗ

Eval golden, GitLab CI, Kafka scout events, OpenTelemetry.