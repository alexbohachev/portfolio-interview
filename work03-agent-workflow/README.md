# Робота 3 — надійний workflow агента (Java 21, Spring Boot)

**Одне речення:** детермінований 3-кроковий workflow з **checkpoint**, **outbox** і **idempotent stub** — **30/30** fault-сценаріїв у `gradlew test`.

```powershell
.\make.ps1 all                # make all = test
docker compose up -d          # Postgres :5433
.\make.ps1 boot               # :8083
```

## Схема

| Крок | Інструмент | Checkpoint |
|------|------------|------------|
| 1 | `RuleSearchTool` | RULES |
| 2 | `CalculatorTool` | CALCULATE |
| 3 | Outbox → `ExternalStubService` | EXTERNAL + COMPLETED |

**Idempotency:** `unique(tenant_id, idempotency_key)` + **command_hash** (SHA-256 канонічного JSON).

## API

```http
POST /api/v1/applications
Content-Type: application/json

{
  "tenantId": "tenant_a",
  "idempotencyKey": "key-1",
  "equipmentType": "sprayer",
  "requestedHours": 6,
  "region": "north"
}
```

## Тести (ТЗ fault)

| Файл | Що покриває |
|------|-------------|
| `WorkflowFaultIT` | idempotency, 409 |
| `WorkflowFaultScenariosIT` | checkpoint resume, crash recovery, validation |
| `WorkflowFaultPostgresIT` | PostgreSQL (`-Dwork03.docker=true`) |

Деталі: [`REPORT.md`](REPORT.md), [`manifests/fault_manifest.json`](manifests/fault_manifest.json).

## Git-tag

```bash
git tag -a work03-v1.0 -m "Work03: workflow outbox idempotency fault tests"
```