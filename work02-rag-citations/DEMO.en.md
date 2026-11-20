[Українська](DEMO.md) | **English**

# Demo work02 (3–5 min, offline)

## Preparation

```powershell
cd c:\Portfolio\work02-rag-citations
py -3.13 -m pip install -r requirements.txt
.\make.ps1 all
.\scripts\demo.ps1
```

## Script

1. Show `REPORT.en.md` / `artifacts/results.json` — Recall@5, QA, gate.
2. Explain **hybrid RRF** vs BM25 (the candidate is no worse on the synthetic corpus — 1.0/1.0).
3. **Refusal:** a threshold on dev, not a prompt (`gate_tune`).
4. (Optional) `$env:OPENAI_API_KEY` → `.\make.ps1 eval-llm`.

## Key phrase

"Refusal is code and a retrieval score, not an instruction in the system prompt."
