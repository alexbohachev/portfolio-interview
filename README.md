# Портфоліо співбесіди (7 робіт)

Monorepo для плану «Python / Java / AI / ML». Кожна робота — окрема директорія з власним `README`, `REPORT.md` і git-tag після завершення.

**Порядок:** 1 → 2 → 3 → 7 → 4 → 5 → 6 (див. `unpacked_docx/` або `.docx` у корені).

## Роботи

| № | Каталог | Статус |
|---|---------|--------|
| 1 | [`work01-bank-marketing/`](work01-bank-marketing/) | **tag** `work01-v1.0` |
| 2 | [`work02-rag-citations/`](work02-rag-citations/) | retrieval + QA offline; LLM judge; `sources.yaml` |
| 3 | [`work03-agent-workflow/`](work03-agent-workflow/) | **30/30** fault IT |
| 7 | [`work07-ai-platform/`](work07-ai-platform/) | **фінальний eval** — tag `work07-v1.0` після коміту |
| 4 | [`work04-ml-serving/`](work04-ml-serving/) | старт: train + FastAPI + rollback test |
| 5 | [`work05-docguard/`](work05-docguard/) | gateway ACL + retrieval filter, 4 security IT |
| 6 | [`work06-bible-rag/`](work06-bible-rag/) | заготовка README |

## Наступні віхи (план)

1. **work02-v1.0** — фінальний test + (опційно) LLM eval
2. **work03-v1.0** — `make all` + tag
3. **work07-v1.0** — `finalize` виконано; демо-відео + git tag
4. **work04** — `make all` + CI  
5. Теги **work02-v1.0**, **work03-v1.0**, **work07-v1.0** (коміт)

## Запуск (робота 1)

Windows:

```powershell
cd work01-bank-marketing
py -3.13 -m pip install -r requirements.txt
py -3.13 -m work01 all
```

## Стандарт

Усі роботи: одна команда повного циклу, baseline + candidate, незалежний test, `REPORT.md`, lock-файли залежностей.