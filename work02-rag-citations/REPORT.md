# Звіт — робота 2: RAG із цитатами

## Задача
Retrieval (BM25 vs hybrid RRF) + retrieval gate + відповідь з цитатами (extractive offline / LLM за ключем).

## Корпус
- документів: 200, fingerprint `21de45e90e9664b3`
- test golden sha: `0993914458593c21`

## Retrieval (test)
| Система | Recall@5 | n |
| baseline BM25 | 1.0000 | 40 |
| candidate hybrid | 1.0000 | 40 |

**Retrieval gate** (поріг max RRF на dev): `0.0313`

## QA (test, candidate + gate)
- Коректні відмови: 10 / 10
- Точність цитат (overlap evidence): 35 / 35
- Відповідь містить gold-фрагмент: 28 / 28

## Обмеження
- Синтетичний корпус 200 docs; LLM вимкнено за замовчуванням.
- Промпт не замінює retrieval gate (відмова лише в коді за порогом).

## Наступний крок
- `.\make.ps1 plan-corpus` → відкритий корпус 200–500 + ручний golden; `.\make.ps1 eval-llm` (30 dev).

_Час: 6.93 с._
