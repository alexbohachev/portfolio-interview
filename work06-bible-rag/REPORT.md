[**Українська**](REPORT.md) | [English](REPORT.en.md)

# Звіт — робота 6 (Bible RAG)

## Обсяг
- SQLite: 30 віршів × 3 переклади (90 рядків); golden dev/test по 15
- Embeddings: **intfloat/multilingual-e5-small**, FAISS CPU
- Eval (test): **Recall@5 = 1.0** (n=15)
- **API** FastAPI `/v1/ask`, **Streamlit** UI, extractive відповідь за замовчуванням

## Команди
```powershell
.\make.ps1 all
.\make.ps1 serve
.\make.ps1 ui
```

## LLM (опційно)
- За замовчуванням `extractive` (цитати з топ-хітів)
- `requirements-llm.txt` + `WORK06_USE_LLM=1` — Qwen2.5-0.5B CPU demo (production ТЗ: **3B 4bit** + CUDA)

## Backlog
- Реальні переклади (ліцензії в `DATA.md`)
- Qwen2.5-3B 4bit на GPU, 60 golden вручну