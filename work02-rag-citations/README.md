# Робота 2 — RAG із цитатами (retrieval)

**Стан:** MVP offline — BM25 vs hybrid (dense + RRF), Recall@5 за evidence spans. LLM — у `config/default.yaml` (`llm.enabled: false`).

```powershell
py -3.13 -m pip install -r requirements.txt
py -3.13 -m work02 seed
.\make.ps1 all
```

Корпус зараз **40 синтетичних agri .md** (розширити до 200–500 відкритих джерел за `DATA.md`). Golden **60** питань (автоген з корпусу); далі — ручна розмітка до 100.

## Команди

| Команда | Дія |
|---------|-----|
| `work02 seed` | корпус + `data/golden/questions.json` |
| `make.ps1 all` | оцінка baseline/candidate |
| `make.ps1 test` | pytest |