# Демо work07 (5–7 хв для запису екрана)

## Перед записом

1. Docker Desktop запущений.
2. (Опційно) LLM: `$env:OPENAI_API_KEY="sk-..."` у тій самій сесії PowerShell.
3. `cd c:\Portfolio\work07-ai-platform`
4. `.\make.ps1 all` — дочекатися **OK smoke**.

## Сценарій демо

| Хв | Дія | Що показати |
|----|-----|-------------|
| 0:00 | `docker compose ps` | 8 сервісів **healthy** |
| 0:30 | Браузер / curl `GET :8090/health` | `indexed_docs` ≈ **200** (корпус work02) |
| 1:00 | `POST :8090/v1/knowledge/search` mode **hybrid** | топ-хіт `agri_*_wheat_disease_*` |
| 2:00 | `POST :8084/api/v1/knowledge/qa` | **answer** + **citations[]** |
| 3:00 | `POST :8082/api/v1/observations` | scout створює спостереження |
| 3:30 | `POST :8084/api/v1/equipment-requests` | Java → Python, `searchMode: hybrid` |
| 4:00 | Заголовок `X-Search-Profile: slow` vs `fast` | кейс продуктивності ([`PERFORMANCE.md`](PERFORMANCE.md)) |
| 4:15 | Jaeger http://localhost:16687 | trace logistics → rag-api |
| 4:30 | Питання «Чи є дані про Марс?» → `qa` | **refused: true** (gate/немає в корпусі) |
| 5:30 | README: схема Java↔Python↔ES | підсумок для інтерв'ю |

## Команди (PowerShell)

```powershell
.\scripts\demo.ps1
```

Або вручну — див. `scripts\demo.ps1`.

## Що сказати інтерв'юеру

- **Hybrid:** BM25 + dense у ES, злиття **RRF** (як work02).
- **Відмова:** не в корпусі → `refused` (не покладаємось лише на промпт).
- **Java:** logistics викликає rag-api через **RestClient** (подальший OpenAPI-клієнт).