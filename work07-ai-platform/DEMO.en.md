[Українська](DEMO.md) | **English**

# Demo work07 (5–7 min for a screen recording)

## Before recording

1. Docker Desktop is running.
2. (Optional) LLM: `$env:OPENAI_API_KEY="sk-..."` in the same PowerShell session.
3. `cd c:\Portfolio\work07-ai-platform`
4. `.\make.ps1 all` — wait for **OK smoke**.

## Demo script

| Min | Action | What to show |
|-----|--------|--------------|
| 0:00 | `docker compose ps` | 8 services **healthy** |
| 0:30 | Browser / curl `GET :8090/health` | `indexed_docs` ≈ **200** (work02 corpus) |
| 1:00 | `POST :8090/v1/knowledge/search` mode **hybrid** | top hit `agri_*_wheat_disease_*` |
| 2:00 | `POST :8084/api/v1/knowledge/qa` | **answer** + **citations[]** |
| 3:00 | `POST :8082/api/v1/observations` | scout creates an observation |
| 3:30 | `POST :8084/api/v1/equipment-requests` | Java → Python, `searchMode: hybrid` |
| 4:00 | Header `X-Search-Profile: slow` vs `fast` | performance case ([`PERFORMANCE.md`](PERFORMANCE.md)) |
| 4:15 | Jaeger http://localhost:16687 | trace logistics → rag-api |
| 4:30 | Question "Is there data about Mars?" → `qa` | **refused: true** (gate / not in the corpus) |
| 5:30 | README: Java↔Python↔ES diagram | interview summary |

## Commands (PowerShell)

```powershell
.\scripts\demo.ps1
```

Or manually — see `scripts\demo.ps1`.

## What to tell the interviewer

- **Hybrid:** BM25 + dense in ES, merged with **RRF** (as in work02).
- **Refusal:** not in the corpus → `refused` (we do not rely on the prompt alone).
- **Java:** logistics calls rag-api through **RestClient** (a generated OpenAPI client later).
