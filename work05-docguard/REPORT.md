# Звіт — робота 5 (DocGuard MVP)

## Задача

Контроль доступу до фрагментів корпусу **до** формування відповіді; audit log; degraded mode без Python.

## Автоматизовано

**4 / 8** сценаріїв у `SecurityMatrixIT` (див. manifest).

## Архітектура

```text
Client → Gateway (ACL + cache + audit) → Python retrieval (filter doc_id)
```

## Наступний крок

Контрактні тести OpenAPI, revoke cache, навантаження 10 хв @ 1 RPS, решта матриці безпеки.