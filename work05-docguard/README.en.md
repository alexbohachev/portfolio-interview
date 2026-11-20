[Українська](README.md) | **English**

# Work 5 — DocGuard (Java + Python)

**MVP:** a Spring Boot **gateway** (ACL, audit, cache) + Python **retrieval** with an `allowed_doc_ids` filter applied before the answer.

```powershell
cd c:\Portfolio\work05-docguard
.\make.ps1 all          # unit IT + docker smoke (if Docker is available)
.\make.ps1 compose-up
.\make.ps1 smoke
.\make.ps1 load         # ~1 RPS, 60 s
```

```powershell
# Python retrieval (separate process)
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

> Identity is taken from the `X-Tenant-Id` / `X-Principal-Id` headers and is **not authenticated by the service**: in a real system a trusted proxy/IdP must set them.

Matrix: `manifests/security_matrix.json` · ACL: `config/acl.yaml`

[`REPORT.en.md`](REPORT.en.md) · [`docs/ADR.en.md`](docs/ADR.en.md)
