[Українська](DATA.md) | **English**

# Data — Work 7

| Field | Value |
|------|----------|
| Corpus | `work02-rag-citations/corpus/bundled` (200 agri `.md`, mounted into rag-api) |
| Golden | `data/golden/dev.json` (100) + `test.json` (50) = **150** |
| Provenance dev | work02 dev+test (regression / tuning) |
| Provenance test | 50 new questions from the corpus, no overlap with work02 test in the final run |
| Action catalog | `config/actions_catalog.json` (**30** actions) |
| Recommendations golden | dev 20 + test 20 → `build_recommendation_golden.py` |

## Collecting golden

```powershell
py -3.13 scripts/build_golden_150.py
```

Final Recall@5 / MRR — only on `--split test`.
