# Робота 5 — DocGuard (Java + Python)

**MVP:** Spring Boot **gateway** (ACL, audit, cache) + Python **retrieval** з фільтром `allowed_doc_ids` до відповіді.

```powershell
cd c:\Portfolio\work05-docguard
.\make.ps1 all
```

```powershell
# Python retrieval (окремий процес)
$env:CORPUS_DIR="c:\Portfolio\work02-rag-citations\corpus\bundled"
py -3.13 -m pip install -r python/retrieval/requirements.txt
py -3.13 -m uvicorn main:app --app-dir python/retrieval --port 8097
```

```http
POST /api/v1/query
X-Tenant-Id: tenant_a
X-Principal-Id: alice
{"question":"бура іржа"}
```

Матриця: `manifests/security_matrix.json` · ACL: `config/acl.yaml`

[`REPORT.md`](REPORT.md) · [`docs/ADR.md`](docs/ADR.md)