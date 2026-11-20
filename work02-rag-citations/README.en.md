[Українська](README.md) | **English**

# Work 2 — RAG with Citations

**In one sentence:** on a 200-document agri corpus, hybrid RRF gets **Recall@5 = 1.00** on test (50 questions) versus **BM25 = 1.00**; with the **retrieval gate**: **10/10** correct refusals, **35/35** citations, **28/28** extractive answers (offline).

```powershell
py -3.13 -m pip install -r requirements.txt
py -3.13 -m work02 seed
py -3.13 -m work02 lock
.\make.ps1 all
```

## Real corpus: Ukrainian Wikipedia (agronomy)

123 articles from uk.wikipedia.org (CC BY-SA 4.0, `corpus/wiki_uk/`, reproduce with `scripts/fetch_wiki_uk.py`), 55 hand-written questions that contain neither a `doc_id` nor an article title, and 10 unanswerable questions (`data/golden/wiki_uk.json`; `scripts/build_wiki_golden.py` checks that every `answer_snippet` really occurs in the article). Evaluation: `python scripts/eval_wiki_uk.py` → `manifests/wiki_uk_eval.json`.

| System | Recall@5 (95% CI) | Recall@1 |
|---|---|---|
| BM25 | 1.00 [1.00, 1.00] | 0.96 |
| dense, English-only `all-MiniLM-L6-v2` | 0.27 [0.16, 0.40] | 0.15 |
| dense, multilingual `paraphrase-multilingual-MiniLM-L12-v2` | 0.65 [0.53, 0.78] | 0.53 |
| hybrid RRF (BM25 + English-only) | 0.64 [0.51, 0.76] | 0.49 |
| hybrid RRF (BM25 + multilingual) | 0.80 [0.69, 0.89] | 0.65 |
| hybrid (multilingual) + cross-encoder `mmarco-mMiniLMv2` | 0.95 [0.87, 1.00] | 0.95 |

Conclusions the data supports (paired 95% CI of the Recall@5 lift):
* The English-only dense model barely works on Ukrainian text (0.27). Swapping it for a multilingual one in the hybrid gives +0.16 [0.04, 0.29].
* The multilingual cross-encoder on top of the hybrid gives +0.15 [0.05, 0.24]: here the re-ranker lift is statistically different from zero (it was not on the synthetic corpus with English-only models).
* **Hybrid with the English-only model is worse than plain BM25** (−0.36 [−0.49, −0.24]): a weak dense model hurts inside RRF.

**Limitations without which the numbers cannot be read:**
* The questions are lexically close to the articles (on average 80% of their tokens appear in the target article), so BM25 reaches 1.00 and the best system here is plain BM25. The set barely tests semantic search; a harder paraphrase set is needed.
* Labels are single-target (one target article); other relevant articles are not counted.
* Whole articles are embedded and the models truncate long inputs; 123 documents and 55 questions: read the intervals, not the point values.
* Refusal gate (maximum cosine similarity of the multilingual model, threshold from dev, checked on test, stratified split): test accuracy 0.91, but only 2 of 5 unanswerable questions were refused, with 0 false refusals out of 28. The sample is too small, and a gate on this signal is weak.

## Evaluation limitations

The answerable part of the golden set was generated from a template and contains the `doc_id` ("…per document agri_001_…"), so Recall@5 = 1.0 and citations 35/35 are lookups by identifier, not a measure of semantic search; the out-of-domain questions are obviously foreign (Mars, cryptocurrency), so 10/10 refusals is also an easy test. The metrics are computed by code and reproducible, but on this corpus they do not distinguish the methods.

## Architecture

```text
query → hybrid retrieval → gate (max RRF, dev) → extractive/LLM → citations (doc_id + span)
```

| Layer | Baseline | Candidate |
|-------|----------|-----------|
| Retrieval | BM25 top-5 | BM25 + dense + RRF |
| Refusal | — | threshold on dev (not a prompt) |
| Answer | — | extractive "quote"; `OPENAI_API_KEY` + `llm.enabled: true` |

## Commands

| Command | Action |
|---------|--------|
| `work02 seed` | 200 docs + golden dev/test (100) |
| `work02 lock` | config_hash in the manifest |
| `make.ps1 all` | retrieval + QA report |

Data details: [`DATA.md`](DATA.md). Report: [`REPORT.md`](REPORT.md).

## Next, per the assignment

- Replace the synthetic corpus with **open** 200–500 sources.
- Enable the LLM + **30 manual** judge ratings.
- Ready for **`work02-v1.0`**: `make all` + `lock` + pytest (open corpus is backlog).
