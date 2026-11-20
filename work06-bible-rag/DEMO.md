[**Українська**](DEMO.md) | [English](DEMO.en.md)

# Демо work06 (3–5 хв)

## Перед записом

```powershell
cd c:\Portfolio\work06-bible-rag
py -3.13 -m pip install -r requirements.txt
.\make.ps1 all
.\make.ps1 serve
```

Інший термінал: `.\scripts\demo.ps1` або `.\make.ps1 ui` для Streamlit.

## Сценарій

| Час | Дія | Показати |
|-----|-----|----------|
| 0:00 | `GET /health` | `index_ready: true`, `corpus_version` |
| 0:45 | `POST /v1/ask` Gen.1.1 | `citations[]`, `mode: extractive` |
| 1:30 | Інший переклад `uk_rb95_stub` | той самий `osis_id`, інший текст |
| 2:15 | Streamlit UI | вибір перекладу, top-K |
| 3:00 | (опційно) LLM checkbox + `WORK06_USE_LLM` | або пояснити backlog 3B 4bit |

## Що сказати інтерв'юеру

- **Offline-first:** SQLite + FAISS, без хмари для retrieval.
- **E5** з префіксами `query:` / `passage:` (як у best practice dense retrieval).
- **Цитати:** відповідь прив'язана до `osis_id`, не «вільна фантазія» (extractive MVP).