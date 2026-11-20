[Українська](REPORT.md) | **English**

# Report — work 1: model training and evaluation

## Task
Binary classification of deposit subscription (UCI Bank Marketing, `bank-full.csv`), the `duration` feature is excluded.

## Data
- SHA-256 of `bank-full.csv`: `d1513ec63b385506f7cfce9f2c5caa9fe99e7ba4e8c3fa264b3aaf0f849ed32d`
- Test: 6782 examples (fixed temporal split, `manifests/test_manifest.json`)
- Share of `yes`: train 0.0581, val 0.1152, test 0.3934 (temporal shift)

## Method
- **Baseline:** logistic regression (`class_weight=balanced`), macro-F1 threshold tuned on validation
- **Candidate:** MLP + early stopping (val macro-F1), temperature scaling on validation, seed 44 chosen by val macro-F1
- **Ablation:** candidate with a fixed threshold of 0.5 (no tuning) — for comparison

## Results (test, single run)

| Metric | Baseline | Candidate |
|---------|----------|-----------|
| macro-F1 | 0.5379 | 0.5377 |
| Brier | 0.2599 | 0.2683 |
| PR-AUC | 0.4969 | 0.4807 |

Thresholds (tuned on val): baseline=0.73, candidate=0.69.

### Ablation: candidate, threshold 0.5
- macro-F1=0.5793, Brier=0.2683, PR-AUC=0.4807

## Training instability (5 seeds, **validation** macro-F1)

- values: [0.5946, 0.6048, 0.5976, 0.6068, 0.602]
- std: 0.0045

## Bootstrap of macro-F1 difference (candidate − baseline, test, fixed thresholds)

- Point estimate: -0.0002
- 95% CI: [-0.0085, 0.0089]

## Error analysis (candidate)

- Errors on test: 2628 / 6782 (38.8%)

**Groups (all errors on test):**

- FN_borderline_high: 899
- FN_mid_score: 645
- FP_high_confidence: 551
- FN_low_score: 411
- FP_borderline: 122

**Examples reviewed (up to 20):**

- row 40397: true=yes, pred=no, p=0.450, FN_borderline_high, age=37, month=jul
- row 40069: true=yes, pred=no, p=0.250, FN_mid_score, age=39, month=jun
- row 43366: true=no, pred=yes, p=0.985, FP_high_confidence, age=82, month=mar
- row 44090: true=yes, pred=no, p=0.001, FN_low_score, age=37, month=jul
- row 43456: true=no, pred=yes, p=0.748, FP_borderline, age=56, month=apr
- row 42740: true=yes, pred=no, p=0.450, FN_borderline_high, age=42, month=jan
- row 42482: true=yes, pred=no, p=0.251, FN_mid_score, age=72, month=dec
- row 42075: true=no, pred=yes, p=0.984, FP_high_confidence, age=84, month=oct
- row 44531: true=yes, pred=no, p=0.001, FN_low_score, age=34, month=aug
- row 44544: true=no, pred=yes, p=0.748, FP_borderline, age=27, month=aug
- row 42723: true=yes, pred=no, p=0.451, FN_borderline_high, age=63, month=jan
- row 44080: true=yes, pred=no, p=0.252, FN_mid_score, age=30, month=jul
- row 45048: true=no, pred=yes, p=0.982, FP_high_confidence, age=69, month=oct
- row 44859: true=yes, pred=no, p=0.002, FN_low_score, age=31, month=sep
- row 40852: true=no, pred=yes, p=0.748, FP_borderline, age=71, month=aug
- row 44057: true=yes, pred=no, p=0.451, FN_borderline_high, age=32, month=jul
- row 43734: true=yes, pred=no, p=0.253, FN_mid_score, age=27, month=may
- row 42027: true=no, pred=yes, p=0.982, FP_high_confidence, age=74, month=oct
- row 44490: true=yes, pred=no, p=0.003, FN_low_score, age=31, month=aug
- row 42977: true=no, pred=yes, p=0.748, FP_borderline, age=38, month=feb

### Conclusions from the errors
1. **Temporal shift** — test has a much higher share of `yes`; the threshold from val is often too high for test.
2. **FN_borderline** — the model underestimates `yes` in the more recent period (campaigns/seasonality of `month`).
3. **FP_high_confidence** — rare re-confirmations of `yes` when the actual label is `no`, after calibration.

## Limitations
- A single final test run; thresholds are fixed from validation.
- Temperature scaling does not fully compensate for the covariate shift between val and test.
- The MLP has no explicit cross-features; logistic regression is strong on tabular data.

## Next step
- Temporal re-fit / a separate calibrator on the latest window; or a model with an explicit `month`/campaign time feature.

_Auto-generated; `make all` time: ~50.34 s._
