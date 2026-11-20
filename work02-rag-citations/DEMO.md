[**Українська**](DEMO.md) | [English](DEMO.en.md)

# Демо work02 (3–5 хв, offline)

## Підготовка

```powershell
cd c:\Portfolio\work02-rag-citations
py -3.13 -m pip install -r requirements.txt
.\make.ps1 all
.\scripts\demo.ps1
```

## Сценарій

1. Показати `REPORT.md` / `artifacts/results.json` — Recall@5, QA, gate.
2. Пояснити **hybrid RRF** vs BM25 (кандидат не гірший на синтетиці — 1.0/1.0).
3. **Відмова:** поріг на dev, не промпт (`gate_tune`).
4. (Опційно) `$env:OPENAI_API_KEY` → `.\make.ps1 eval-llm`.

## Ключова фраза

«Відмова — це код і retrieval score, а не інструкція в system prompt».