[Українська](DEMO.md) | **English**

# Demo work05 (4–6 min)

```powershell
cd c:\Portfolio\work05-docguard
docker compose up -d --build
.\make.ps1 smoke
```

## Script

| Step | What to show |
|------|--------------|
| 1 | `GET http://localhost:8097/health` — docs=200 |
| 2 | `alice` → allowed `agri_*` hits |
| 3 | Mock leak / IT: `403 leak blocked` in the SecurityMatrixIT report |
| 4 | `POST /api/v1/admin/invalidate-cache` — a second retrieval |
| 5 | Audit + prompt injection preserved in the log |

```powershell
.\make.ps1 load
.\scripts\reliability_demo.ps1
```

**Thesis:** ACL + `doc_id` filter **before** the answer; degraded mode without Python.
