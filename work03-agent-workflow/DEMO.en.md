[Українська](DEMO.md) | **English**

# Demo work03 (3–5 min)

## Preparation

```powershell
cd c:\Portfolio\work03-agent-workflow
.\make.ps1 all
docker compose up -d
.\make.ps1 boot
```

Another terminal: `.\scripts\demo.ps1` · live reliability: `.\scripts\reliability_demo.ps1` (requires `.\make.ps1 boot`).

## Script

| Time | Action |
|------|--------|
| 0:00 | `manifests/fault_manifest.json` — **30/30** fault ITs |
| 1:00 | `POST /api/v1/applications` — happy path |
| 2:00 | Repeat with the same `idempotencyKey` — the same response |
| 3:00 | Invalid payload → **400** |

## Thesis

Checkpoint + outbox + idempotency (hash) — recovery without duplicating external calls.
