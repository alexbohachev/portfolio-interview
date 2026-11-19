# Демо work05 (4–6 хв)

```powershell
cd c:\Portfolio\work05-docguard
docker compose up -d --build
.\make.ps1 smoke
```

## Сценарій

| Крок | Що показати |
|------|-------------|
| 1 | `GET http://localhost:8097/health` — docs=200 |
| 2 | `alice` → дозволені `agri_*` хіти |
| 3 | Mock leak / IT: `403 leak blocked` у звіті SecurityMatrixIT |
| 4 | `POST /api/v1/admin/invalidate-cache` — другий retrieval |
| 5 | Audit + prompt injection збережено в лог |

```powershell
.\make.ps1 load
```

**Тезис:** ACL + фільтр `doc_id` **до** відповіді; degraded без Python.