# Звіт — робота 3 (чернетка)

## Статус

- Детермінований workflow із checkpoint у PostgreSQL
- Інтеграційні fault-тести: idempotency, command_hash conflict
- LLM і розширений fault-набір — у наступній ітерації

## Test (JUnit + Testcontainers)

| Сценарій | Результат |
|----------|-----------|
| Дубль idempotency_key | 1 external effect |
| Конфлікт command_hash | HTTP 409 |

_Оновлюється після `.\make.ps1 all`._