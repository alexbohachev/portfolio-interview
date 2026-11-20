[Українська](DATA.md) | **English**

# Data — work 2

| Field | Value |
|------|----------|
| MVP corpus | 200 synthetic `.md` files in `corpus/bundled/` (CC0, for pipeline debugging) |
| Spec target | 200–500 **open** agricultural documents with licenses listed in this file |
| Golden | `data/golden/dev.json` (50) + `test.json` (50) ≈ 100 questions |
| Types | single_doc, multi_hop, unanswerable (stratified dev/test) |

## Replacing the corpus with an open one (next stage)

1. Add `data/sources.yaml` with URL, license, download date.
2. Script `scripts/fetch_corpus.py` → `corpus/raw/` → normalization into `corpus/bundled/`.
3. Recompute `corpus_fingerprint` and a **new** golden (manual labeling of evidence spans).

## Licenses (plan)

See also [`data/sources.yaml`](data/sources.yaml).

| Source | License | Status |
|---------|----------|--------|
| Synthetic agri MVP | CC0 | in the repository |
| FAO / extension factsheets | check per URL | in sources.yaml |

Golden **test** does not change after `work02 lock` without a new manifest.
