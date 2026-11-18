# Робота 3 — надійний workflow агента (Java 21, Spring Boot)

**Сценарій:** заявка на техніку — 3 інструменти (правила, калькулятор, зовнішній запис), checkpoint після кожного кроку в PostgreSQL, **idempotency_key** + **command_hash**.

```powershell
docker compose up -d          # опційно, порт 5433
.\make.ps1 all                # Testcontainers + fault tests
.\make.ps1 boot               # API :8083
```

## API

```http
POST /api/v1/applications
{
  "tenantId": "tenant_a",
  "idempotencyKey": "key-1",
  "equipmentType": "sprayer",
  "requestedHours": 6,
  "region": "north"
}
```

## Поведінка (ТЗ)

| Кейс | Очікування |
|------|------------|
| Повтор тієї ж заявки (key + hash) | Той самий результат, **1** запис у `external_effects` |
| Той самий key, інший hash | **409 Conflict** |
| Checkpoint | Після кожного кроку `saveAndFlush` — можна відновити |

**Baseline:** детермінований workflow без LLM-планувальника (кроки фіксовані).

## Далі за ТЗ

- Outbox + симуляція падіння після commit зовнішньої системи
- LLM-планувальник (Spring AI) як candidate
- 30 fault-сценаріїв у звіті