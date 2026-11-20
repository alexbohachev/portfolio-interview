[Українська](DEMO.md) | **English**

# Demo work01 (2–4 min, offline)

## Preparation

```powershell
cd c:\Portfolio\work01-bank-marketing
py -3.13 -m pip install -r requirements.txt
.\make.ps1 all
.\scripts\demo.ps1
```

## Script

1. **Data:** UCI Bank Marketing, **without `duration`** (leakage).
2. **Temporal split** + bootstrap CI of the macro-F1 difference.
3. **Baseline LR** vs **candidate MLP** + temperature scaling.
4. Show `REPORT.en.md` — test metrics and the 0.5-threshold ablation.

## Interview message

"The candidate does not beat the baseline on test, and that is documented; what matters are stability, the ablation and an honest report."
