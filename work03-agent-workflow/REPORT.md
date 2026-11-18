# Звіт — робота 3: надійний workflow агента

## Задача

Заявка на техніку: **3 інструменти** (правила, калькулятор, зовнішній запис), PostgreSQL checkpoint, idempotency_key + command_hash, **outbox** перед зовнішнім ефектом.

## Baseline

Детермінований порядок кроків без LLM-планувальника.

## Архітектура

```text
POST /applications → WorkflowRun (checkpoint) → Outbox PENDING → Stub (idempotent) → COMPLETED
                              ↑_________________recovery if effect exists________________|
```

## Fault-сценарії (JUnit, профіль `test`)

| # | Сценарій | Очікування | Статус |
|---|----------|------------|--------|
| 1 | Повтор idempotency_key | 1 `external_effects` | pass |
| 2 | Той самий key, інший hash | HTTP 409 | pass |
| 3 | Restart з checkpoint CALCULATE | COMPLETED, 1 effect | pass |
| 4 | Effect уже в БД, workflow не завершений | 1 effect, checkpoint добивається | pass |
| 5 | Новий key, ті самі аргументи | 2 effects (дозволено доменом) | pass |
| 6 | Невалідний вхід | 400, workflow не створюється | pass |

**6 / 6** автоматизованих сценаріїв (ціль ТЗ — 30; решта — у backlog: outbox retry, budget, human approval).

## Метрики (MVP)

- Дубльовані зовнішні ефекти на fault-тестах idempotency: **0 / n** (n=2 повтори)
- Успішне завершення на сценаріях 1–5: **5 / 5**

## Обмеження

- Outbox без окремого воркера/черги (публікація синхронна в тій самій транзакції).
- LLM-планувальник не підключений (candidate).

## Наступний крок

- Spring AI candidate, human-in-the-loop, 24 додаткових fault-кейси + Testcontainers PostgreSQL у CI.

_Оновлено після `.\make.ps1 all`._