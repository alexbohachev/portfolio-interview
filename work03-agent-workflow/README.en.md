[Українська](README.md) | **English**

# Work 3 — Reliable Agent Workflow (Java 21, Spring Boot)

**In one sentence:** a deterministic 3-step workflow with **checkpoints**, an **outbox** and an **idempotent stub** — **30/30** fault scenarios in `gradlew test`.

```powershell
.\make.ps1 all                # make all = test
docker compose up -d          # Postgres :5433
.\make.ps1 boot               # :8083
```

## Outline

| Step | Tool | Checkpoint |
|------|------|------------|
| 1 | `RuleSearchTool` | RULES |
| 2 | `CalculatorTool` | CALCULATE |
| 3 | Outbox → `ExternalStubService` | EXTERNAL + COMPLETED |

**Idempotency:** `unique(tenant_id, idempotency_key)` + **command_hash** (SHA-256 of the canonical JSON).

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

## Tests (fault assignment)

| File | What it covers |
|------|----------------|
| `WorkflowFaultIT` | idempotency, 409 |
| `WorkflowFaultScenariosIT` | checkpoint resume, crash recovery, validation |
| `WorkflowFaultPostgresIT` | PostgreSQL (`-Dwork03.docker=true`) |

Details: [`REPORT.md`](REPORT.md), [`manifests/fault_manifest.json`](manifests/fault_manifest.json).

## Git tag

```bash
git tag -a work03-v1.0 -m "Work03: workflow outbox idempotency fault tests"
```
