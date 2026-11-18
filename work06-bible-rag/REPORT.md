# Звіт — робота 6 (Bible RAG MVP)

## Обсяг MVP
- SQLite: synthetic 30×3 переклади (90 рядків) + golden dev/test по 15
- Embeddings: **intfloat/multilingual-e5-small**, FAISS CPU
- Eval (test): **Recall@5 = 1.0** (n=15)

## Команда
```powershell
cd work06-bible-rag
py -3.13 -m pip install -r requirements.txt
.\make.ps1 all
```

## Backlog (ТЗ)
- Реальні переклади + `DATA.md` ліцензії
- Qwen2.5-3B 4bit + Streamlit UI