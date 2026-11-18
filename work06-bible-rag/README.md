# Робота 6 — Локальний RAG (Біблія)

**MVP:** SQLite (3 переклади-stub) → FAISS + **multilingual-e5** → FastAPI + Streamlit.

## Швидкий старт

```powershell
py -3.13 -m pip install -r requirements.txt
.\make.ps1 all
```

```powershell
.\make.ps1 serve    # API http://127.0.0.1:8098
.\make.ps1 ui       # Streamlit
```

`POST /v1/ask` — JSON `{"question":"...", "top_k":5, "use_llm":false}`

Опційний LLM: `pip install -r requirements-llm.txt`, `$env:WORK06_USE_LLM="1"` (повний ТЗ: Qwen2.5-3B 4bit на GPU).

## Команди

`seed` · `index` · `eval` · `lock` · `test` · `serve` · `ui` · `all`

Docker (після `make.ps1 all`): `docker compose up --build` → порт **8098**.

[`REPORT.md`](REPORT.md) · [`DATA.md`](DATA.md)