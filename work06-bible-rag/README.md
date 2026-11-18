# Робота 6 — Локальний RAG (Біблія)

**MVP:** SQLite → FAISS + **multilingual-e5-small**, golden recall offline.

## Швидкий старт (Windows)

```powershell
py -3.13 -m pip install -r requirements.txt
.\make.ps1 all
```

Цілі: `seed` · `index` · `eval` · `test`

## Структура

- `config/default.yaml` — шляхи БД/індексу, модель
- `scripts/` — init, seed, build_index, eval_recall
- `data/golden/` — dev/test JSON
- `REPORT.md` — останні метрики

Повний ТЗ: LLM + Streamlit — у backlog (`REPORT.md`).