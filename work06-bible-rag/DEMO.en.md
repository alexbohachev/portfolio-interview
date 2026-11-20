[Українська](DEMO.md) | **English**

# Demo work06 (3–5 min)

## Before recording

```powershell
cd c:\Portfolio\work06-bible-rag
py -3.13 -m pip install -r requirements.txt
.\make.ps1 all
.\make.ps1 serve
```

Another terminal: `.\scripts\demo.ps1` or `.\make.ps1 ui` for Streamlit.

## Script

| Time | Action | Show |
|------|--------|------|
| 0:00 | `GET /health` | `index_ready: true`, `corpus_version` |
| 0:45 | `POST /v1/ask` Gen.1.1 | `citations[]`, `mode: extractive` |
| 1:30 | Another translation `uk_rb95_stub` | the same `osis_id`, different text |
| 2:15 | Streamlit UI | translation selection, top-K |
| 3:00 | (optional) LLM checkbox + `WORK06_USE_LLM` | or explain the 3B 4-bit backlog |

## What to tell the interviewer

- **Offline-first:** SQLite + FAISS, no cloud for retrieval.
- **E5** with the `query:` / `passage:` prefixes (as in dense retrieval best practice).
- **Citations:** the answer is tied to an `osis_id`, not "free invention" (extractive MVP).
