[Українська](README.md) | **English**

# Work 6 — Local RAG (Bible)

**MVP:** SQLite (3 stub translations) → FAISS + **multilingual-e5** → FastAPI + Streamlit.

## Quick start

```powershell
py -3.13 -m pip install -r requirements.txt
.\make.ps1 all
```

```powershell
.\make.ps1 serve    # API http://127.0.0.1:8098
.\make.ps1 ui       # Streamlit
```

`POST /v1/ask` — JSON `{"question":"...", "top_k":5, "use_llm":false}`

Optional LLM: `pip install -r requirements-llm.txt`, `$env:WORK06_USE_LLM="1"` (full assignment: Qwen2.5-3B 4-bit on a GPU).

## Commands

`seed` · `index` · `eval` · `lock` · `test` · `serve` · `ui` · `all`

Docker (after `make.ps1 all`): `docker compose up --build` → port **8098**.

[`REPORT.md`](REPORT.md) · [`DATA.md`](DATA.md)
