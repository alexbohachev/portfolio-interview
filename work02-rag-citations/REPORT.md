# Звіт — робота 2: RAG із цитатами (retrieval MVP)

## Задача
Порівняння BM25 (baseline) і hybrid BM25+dense з RRF (candidate) за Recall@5 для evidence spans.

## Корпус
- документів: 40, chunks: 40
- fingerprint: `3c643190328c6212`

## Результати test

| Система | Recall@5 | n |
| baseline (BM25) | 0.5500 | 20 |
| candidate (hybrid) | 0.8500 | 20 |

## Обмеження
- Offline retrieval only; LLM-відповіді (`llm.enabled`) — наступний крок.
- Synthetic golden set 60 питань; масштабування до 100 з ручною розміткою.

## Наступний крок
- Підключити LLM + citation judge; розширити корпус до 200–500 відкритих агро-текстів.

_Час: 3.62 с._
