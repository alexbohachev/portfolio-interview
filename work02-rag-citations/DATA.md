[**Українська**](DATA.md) | [English](DATA.en.md)

# Дані — робота 2

| Поле | Значення |
|------|----------|
| Корпус MVP | 200 синтетичних `.md` у `corpus/bundled/` (CC0, для відладки пайплайна) |
| Ціль ТЗ | 200–500 **відкритих** агро-документів із ліцензіями в цьому файлі |
| Golden | `data/golden/dev.json` (50) + `test.json` (50) ≈ 100 питань |
| Типи | single_doc, multi_hop, unanswerable (стратифікований dev/test) |

## Заміна корпусу на відкритий (наступний етап)

1. Додати `data/sources.yaml` з URL, ліцензією, датою завантаження.
2. Скрипт `scripts/fetch_corpus.py` → `corpus/raw/` → нормалізація в `corpus/bundled/`.
3. Перерахувати `corpus_fingerprint` і **новий** golden (ручна розмітка evidence spans).

## Ліцензії (план)

Див. також [`data/sources.yaml`](data/sources.yaml).

| Джерело | Ліцензія | Статус |
|---------|----------|--------|
| Synthetic agri MVP | CC0 | у репозиторії |
| FAO / extension factsheets | перевірити per URL | у sources.yaml |

Golden **test** не змінюється після `work02 lock` без нового manifest.