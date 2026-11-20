[Українська](REPORT.md) | **English**

# Report — Work 6 (Bible RAG)

## Scope
- SQLite: 30 verses × 3 translations (90 rows); golden dev/test of 15 each
- Embeddings: **intfloat/multilingual-e5-small**, FAISS CPU
- Eval (test): **Recall@5 = 1.0** (n=15)
- **API** FastAPI `/v1/ask`, **Streamlit** UI, extractive answer by default

## Commands
```powershell
.\make.ps1 all
.\make.ps1 serve
.\make.ps1 ui
```

## LLM (optional)
- Default is `extractive` (quotes from the top hits)
- `requirements-llm.txt` + `WORK06_USE_LLM=1` — Qwen2.5-0.5B CPU demo (production assignment: **3B 4-bit** + CUDA)

## Backlog
- Real translations (licences in [`DATA.en.md`](DATA.en.md))
- Qwen2.5-3B 4-bit on a GPU, 60 hand-made golden items
