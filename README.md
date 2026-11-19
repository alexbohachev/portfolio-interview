# Портфоліо співбесіди (7 робіт)

Monorepo для плану «Python / Java / AI / ML». Кожна робота — окрема директорія з власним `README`, `REPORT.md` і git-tag після завершення.

**Інтерв'ю:** [`INTERVIEW_PREP.md`](INTERVIEW_PREP.md) · [`PORTFOLIO.md`](PORTFOLIO.md) · **EN** [`README.en.md`](README.en.md) · [`REPRO.md`](REPRO.md)

```powershell
.\scripts\repro_check.ps1
.\scripts\live_interview.ps1 work07   # smoke + bench + demo
```

Головний кейс N+1: [`work07-ai-platform/CASE_N1_PERF.md`](work07-ai-platform/CASE_N1_PERF.md).

**Порядок:** 1 → 2 → 3 → 7 → 4 → 5 → 6 (див. `unpacked_docx/` або `.docx` у корені).

## Роботи

| № | Каталог | Статус |
|---|---------|--------|
| 1 | [`work01-bank-marketing/`](work01-bank-marketing/) | **tag** `work01-v1.0` |
| 2 | [`work02-rag-citations/`](work02-rag-citations/) | **tag** `work02-v1.0` |
| 3 | [`work03-agent-workflow/`](work03-agent-workflow/) | **tag** `work03-v1.0` |
| 7 | [`work07-ai-platform/`](work07-ai-platform/) | **tag** `work07-v1.0` |
| 4 | [`work04-ml-serving/`](work04-ml-serving/) | train + FastAPI; `make all` + lock |
| 5 | [`work05-docguard/`](work05-docguard/) | gateway ACL; **8/8** security IT |
| 6 | [`work06-bible-rag/`](work06-bible-rag/) | API + Streamlit; Recall@5 test **1.0** |

## Запуск (приклад)

Windows:

```powershell
cd work06-bible-rag
py -3.13 -m pip install -r requirements.txt
.\make.ps1 all
```

## Стандарт

Усі роботи: одна команда повного циклу, baseline + candidate (де в ТЗ), незалежний test, `REPORT.md`, lock/manifest залежностей.