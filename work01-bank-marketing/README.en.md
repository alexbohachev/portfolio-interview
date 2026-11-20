[Українська](README.md) | **English**

# Work 1 — Model Training and Evaluation

**In one sentence:** on UCI Bank Marketing (without `duration`), logistic regression and a calibrated MLP reach **macro-F1 ≈ 0.538** on the test set; the difference is inside the bootstrap CI **[−0.0085, 0.0089]** (the candidate is not better than the baseline).

## Results (test, thresholds chosen on validation)

| Metric | Baseline | Candidate |
|--------|----------|-----------|
| macro-F1 | 0.5379 | 0.5377 |
| Brier | 0.2599 | 0.2683 |
| PR-AUC | 0.4969 | 0.4807 |

Thresholds: baseline **0.73**, candidate **0.69** (macro-F1 on val). Share of `yes`: train 5.8% → val 11.5% → **test 39.3%**.

```text
[train 5.8% yes] → [val 11.5%] → threshold tuning → [test 39.3% yes] → strong covariate shift
```

## Solution outline

```text
bank-full.csv ──► temporal split ──► OneHot+Scaler
                        ├─► LogReg (baseline) ──► threshold on val ──► test
                        └─► MLP (5 seeds) ──► best seed on val ──► temperature scaling ──► threshold on val ──► test
```

## Three main causes of errors (candidate)

| # | Cause | What was done |
|---|-------|---------------|
| 1 | Temporal shift in the `yes` share (5.8% → 39.3%) | Threshold from val only; the negative result is reported, no tuning on test |
| 2 | Mass **FN** in late `month` values (low p when true = yes) | Grouped in `artifacts/error_cases.json`, 20 rows analysed in `REPORT.md` |
| 3 | Tabular data: logistic regression is strong, the MLP gives no gain | Seed 44 fixed by val; bootstrap shows an effect ≈ 0 |

## Run

```powershell
py -3.13 -m pip install -r requirements.txt
py -3.13 -m work01 lock    # after changing config, before the final test run
.\make.ps1 all             # ~50–60 s on CPU
```

| Command | Action |
|---------|--------|
| `.\make.ps1 data` | Download + SHA-256 |
| `.\make.ps1 test` | pytest (offline) |

Full report: [`REPORT.md`](REPORT.md). Data: [`DATA.md`](DATA.md). Test manifest: [`manifests/test_manifest.json`](manifests/test_manifest.json).

## Completion criteria (assignment)

- [x] `make all` / `make.ps1 all` on a clean machine (after `pip install`)
- [x] manifest + config_hash **before** test (`work01 lock`)
- [x] baseline + candidate + ablation (threshold 0.5)
- [x] 5 seeds — std on **validation**
- [x] bootstrap of the macro-F1 difference on test
- [x] error analysis (≤20 cases)
- [ ] git tag `work01-v1.0` after your review of the report
- [ ] rehearse the 2-minute talk + 3 questions from the assignment table

## Interview hints

- **Why does the CI cross zero?** The candidate's effect is statistically indistinguishable from the baseline at fixed thresholds.
- **Why does the 0.5 ablation have a higher F1 on test?** A threshold chosen on val does not transfer under shift; test was **not** used to pick the threshold.
- **Seed vs bootstrap:** seed spread on val (~0.0045 std); bootstrap is the error on test.

## Git tag

```bash
git tag -a work01-v1.0 -m "Work 1: Bank Marketing, baseline vs MLP, REPORT.md"
```
