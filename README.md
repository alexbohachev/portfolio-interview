# Портфоліо співбесіди (7 робіт)

Monorepo для плану «Python / Java / AI / ML». Кожна робота — окрема директорія з власним `README`, `REPORT.md` і git-tag після завершення.

**Порядок:** 1 → 2 → 3 → 7 → 4 → 5 → 6 (див. `docs/`).

## Роботи

| № | Каталог | Статус |
|---|---------|--------|
| 1 | [`work01-bank-marketing/`](work01-bank-marketing/) | звіт готовий, tag — після рецензії |
| 2 | [`work02-rag-citations/`](work02-rag-citations/) | retrieval MVP |
| 3 | `work03-agent-workflow/` | заплановано |

## Запуск (робота 1)

Windows (без GNU make):

```powershell
cd work01-bank-marketing
py -3.13 -m pip install -r requirements.txt
py -3.13 -m work01 all
```

Linux / macOS / Git Bash:

```bash
cd work01-bank-marketing
make all
```

## Стандарт

Усі роботи: одна команда повного циклу, baseline + candidate, незалежний test, `REPORT.md`, lock-файли залежностей.