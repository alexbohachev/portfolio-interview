[Українська](REPORT.md) | **English**

# Report — Work 5 (DocGuard MVP)

## Task

Access control over corpus fragments **before** the answer is generated; audit log; degraded mode without Python.

## Automated

**8 / 8** scenarios in `SecurityMatrixIT` (see `manifests/security_matrix.json`).

```powershell
cd work05-docguard
.\gradlew.bat test
```

## Architecture

```text
Client → Gateway (ACL + cache + audit) → Python retrieval (filter doc_id)
```

## Live stack

```powershell
docker compose up -d --build
.\make.ps1 smoke
.\make.ps1 load
```

Smoke (live): **3 hits** for `бура іржа` / tenant_a:alice.

Load (30 s @ 1 RPS): **30/30 OK**, p50 **~18 ms**.

Corpus: volume `../work02-rag-citations/corpus/bundled` → retrieval.

OpenAPI (MVP contract): `openapi/gateway.openapi.json`

## Contract

`GatewayResponseShapeIT` (2) + `openapi/gateway.openapi.json`.

## Backlog

RestAssured + full JSON Schema; 10-minute @ 1 RPS load in CI.
