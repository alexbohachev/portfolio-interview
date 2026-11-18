# Робота 7 — AI-платформа (MVP Compose)

Локальний стенд за архітектурою з резюме:

| Сервіс | Порт | Роль |
|--------|------|------|
| farm | 8081 | поля/культури |
| scout | 8082 | спостереження |
| logistics | 8084 | викликає Python RAG |
| rag-api | 8090 | пошук у Elasticsearch |
| worker | — | Kafka → індексація |
| postgres | 5434 | доменні дані (заготовка) |
| elasticsearch | 9200 | індекс знань |
| redpanda | 19092 | Kafka-сумісна черга |

```powershell
.\make.ps1 all    # bootJar → compose build/up → smoke
.\make.ps1 down
```

## MVP vs ТЗ

- [x] 3 Java + 2 Python у Compose
- [x] logistics → rag-api (REST)
- [x] hybrid MVP: BM25 через ES `multi_match` (dense — наступний крок)
- [x] Kafka worker skeleton
- [ ] Q&A + citations + 1 LLM provider
- [ ] Golden 150, GitLab CI, OTel

Деталі: [`REPORT.md`](REPORT.md).