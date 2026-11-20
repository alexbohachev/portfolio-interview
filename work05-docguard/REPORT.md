[**Українська**](REPORT.md) | [English](REPORT.en.md)

# Звіт — робота 5 (DocGuard MVP)

## Задача

Контроль доступу до фрагментів корпусу **до** формування відповіді; audit log; degraded mode без Python.

## Автоматизовано

**8 / 8** сценаріїв у `SecurityMatrixIT` (див. `manifests/security_matrix.json`).

```powershell
cd work05-docguard
.\gradlew.bat test
```

## Архітектура

```text
Client → Gateway (ACL + cache + audit) → Python retrieval (filter doc_id)
```

## Live stack

```powershell
docker compose up -d --build
.\make.ps1 smoke
.\make.ps1 load
```

Smoke (live): **3 hits** для `бура іржа` / tenant_a:alice.

Load (30 с @ 1 RPS): **30/30 OK**, p50 **~18 ms**.

Корпус: volume `../work02-rag-citations/corpus/bundled` → retrieval.

OpenAPI (контракт MVP): `openapi/gateway.openapi.json`

## Контракт

`GatewayResponseShapeIT` (2) + `openapi/gateway.openapi.json`.

## Backlog

RestAssured + повна JSON Schema; load 10 хв@1 RPS у CI.