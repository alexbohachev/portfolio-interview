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

## Backlog

OpenAPI contract tests, load 10 хв @ 1 RPS, docker-compose з живим Python retrieval.