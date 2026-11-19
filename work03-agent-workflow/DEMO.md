# Демо work03 (3–5 хв)

## Підготовка

```powershell
cd c:\Portfolio\work03-agent-workflow
.\make.ps1 all
docker compose up -d
.\make.ps1 boot
```

Інший термінал: `.\scripts\demo.ps1` · live надійність: `.\scripts\reliability_demo.ps1` (потрібен `.\make.ps1 boot`).

## Сценарій

| Час | Дія |
|-----|-----|
| 0:00 | `manifests/fault_manifest.json` — **30/30** fault IT |
| 1:00 | `POST /api/v1/applications` — happy path |
| 2:00 | Повтор з тим самим `idempotencyKey` — та сама відповідь |
| 3:00 | Невалідний payload → **400** |

## Тезис

Checkpoint + outbox + idempotency (hash) — відновлення без дублювання зовнішніх викликів.