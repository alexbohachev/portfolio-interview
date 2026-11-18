# Продуктивність «до / після» (робота 7)

## Проблема (до)

`X-Search-Profile: slow` у `POST /api/v1/equipment-requests` (logistics):

- послідовні hybrid-виклики по **кожному токену** запиту;
- додатково BM25 і hybrid по повному тексту (N+1 до rag-api).

## Виправлення (після)

`X-Search-Profile: fast` (за замовчуванням) — **один** hybrid `topK=3`.

## Замір

```powershell
.\make.ps1 bench    # 25 запитів → artifacts/latency_before_after.json
```

Порівнюйте `p50_ms` / `p95_ms` slow vs fast. Функціонально обидва профілі мають повертати ненульові `knowledgeHits` на агро-запитах із демо.

## k6 (опційно)

Для співбесіди достатньо Python benchmark; k6-скрипт можна додати після MVP.