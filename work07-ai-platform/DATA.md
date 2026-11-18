# Дані — робота 7

| Поле | Значення |
|------|----------|
| Корпус | `work02-rag-citations/corpus/bundled` (200 agri `.md`, mount у rag-api) |
| Golden | `data/golden/dev.json` (100) + `test.json` (50) = **150** |
| Provenance dev | work02 dev+test (регресія / tuning) |
| Provenance test | 50 нових питань з корпусу, без перетину з work02 test у фінальному прогоні |
| Довідник дій | `config/actions_catalog.json` (**30** дій) |
| Рекомендації golden | dev 20 + test 20 → `build_recommendation_golden.py` |

## Збір golden

```powershell
py -3.13 scripts/build_golden_150.py
```

Фінальний Recall@5 / MRR — лише на `--split test`.