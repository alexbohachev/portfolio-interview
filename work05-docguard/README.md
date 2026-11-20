# Робота 5 — DocGuard (Java + Python)

**MVP:** Spring Boot **gateway** (ACL, audit, cache) + Python **retrieval** з фільтром `allowed_doc_ids` до відповіді.

```powershell
cd c:\Portfolio\work05-docguard
.\make.ps1 all          # unit IT + docker smoke (якщо є Docker)
.\make.ps1 compose-up
.\make.ps1 smoke
.\make.ps1 load         # ~1 RPS, 60 с
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

> Ідентичність береться із заголовків `X-Tenant-Id` / `X-Principal-Id` і **сервісом не автентифікується**: у реальній системі їх має виставляти довірений проксі/IdP.

Матриця: `manifests/security_matrix.json` · ACL: `config/acl.yaml`

[`REPORT.md`](REPORT.md) · [`docs/ADR.md`](docs/ADR.md)