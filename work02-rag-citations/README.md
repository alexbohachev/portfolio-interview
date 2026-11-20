# Робота 2 — RAG із цитатами

**Одне речення:** на 200-doc agri корпусі hybrid RRF дає **Recall@5 = 1.00** на test (50 пит.) проти **BM25 = 1.00**; з **retrieval gate** — **10/10** коректних відмов, **35/35** цитат, **28/28** extractive відповідей (offline).

```powershell
py -3.13 -m pip install -r requirements.txt
py -3.13 -m work02 seed
py -3.13 -m work02 lock
.\make.ps1 all
```

## Обмеження оцінки

Запитання answerable-частини golden-набору згенеровані шаблоном і містять `doc_id` («…згідно з документом agri_001_…»), тож Recall@5 = 1.0 і цитати 35/35 є пошуком за ідентифікатором, а не показником семантичного пошуку; запитання поза доменом очевидно чужі (Марс, криптовалюта), тому 10/10 відмов теж легкий тест. Метрики рахуються кодом і відтворюються, але на цьому корпусі вони не відрізняють методи.

## Архітектура

```text
запит → hybrid retrieval → gate (max RRF, dev) → extractive/LLM → цитати (doc_id + span)
```

| Шар | Baseline | Candidate |
|-----|----------|-----------|
| Retrieval | BM25 top-5 | BM25 + dense + RRF |
| Відмова | — | поріг на dev (не промпт) |
| Відповідь | — | extractive «цитата»; `OPENAI_API_KEY` + `llm.enabled: true` |

## Команди

| Команда | Дія |
|---------|-----|
| `work02 seed` | 200 docs + golden dev/test (100) |
| `work02 lock` | config_hash у manifest |
| `make.ps1 all` | retrieval + QA звіт |

Деталі даних: [`DATA.md`](DATA.md). Звіт: [`REPORT.md`](REPORT.md).

## Далі за ТЗ

- Замінити синтетичний корпус на **відкриті** 200–500 джерел.
- Увімкнути LLM + **30 ручних** оцінок judge.
- Готово до **`work02-v1.0`**: `make all` + `lock` + pytest (відкритий корпус — backlog).