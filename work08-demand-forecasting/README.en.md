[Українська](README.md) | **English**

# Work 08: Demand Forecasting & Inventory Optimization

A production-style time-series demand forecasting project for a **Senior ML Engineer** role.

## Key engineering features

1. **Strict leakage-free backtesting and zero train-serving skew (Zero Lookahead & Ex-Ante Alignment):**
   * 4-fold sequential expanding-window backtest on 20 time series (21,920 observations of a calibrated simulation with agro dynamics) across 4 real agricultural seasons (spring sowing, summer care, autumn harvest/sowing, winter off-season).
   * Horizon $H=14$ days: all lags and rolling aggregates are shifted by at least 14 days ($t - H$).
   * Rolling statistics are computed strictly per `hub_id × sku_id` (`groupby transform`) with no leakage across series boundaries.
   * **A single Ex-Ante pipeline (`build_ex_ante_features`):** test folds use exactly the information available to the API at forecast time $T_0$ (last price carried forward, climatological expected temperature without noise, planned promo schedule).
2. **Honest baselines:**
   * Seasonal Naive ($y_{t-7}$) and a Historical Day-of-Week 4-Week Moving Average.
   * On the agro-demand simulation LightGBM beats Seasonal Naive by **40.68% in WAPE** (7.83% vs 13.20% on average across all seasons).
3. **Asymmetric-risk optimization (Newsvendor Inventory Policy) and interval calibration (CQR):**
   * Shortage penalty $C_{under} = 5.0$, holding cost $C_{over} = 1.0$.
   * Quantile boosting at the critical quantile $\tau^* = 83.33\%$ cuts the simulated warehouse cost by **43.06%** (from 7,308.0 to 4,160.9 units).
   * Split-conformal calibration (CQR) delivered **observed coverage $\ge 80.0\%$ on all four synthetic test slices** (mean **84.11%** vs 75.90% uncalibrated).
4. **Validation on real data (Capital Bikeshare) and a Senior ML engineering decision:**
   * On real sensor data (1,456 records, 2011–2012) with a strong non-stationary station-expansion trend, the simple Seasonal Naive baseline beat LightGBM (WAPE 35.42% vs 37.74%; warehouse cost 33,576 vs 51,630 units).
   * **Production decision for Bikeshare:** deploy the Seasonal Baseline (Occam's razor, zero inference and drift-monitoring cost). CQR calibration raised coverage from 26.79% to 75.89% (below 80% because the trend violates exchangeability).
5. **In-depth segment analysis:**
   * Error breakdown by 4 agro seasons (lift from +13.7% to +53.1%), 4 SKU categories, 5 regional hubs, days of the week and promo campaigns.
6. **Production serving (FastAPI):**
   * Endpoints `/v1/health` and `/v1/forecast`.
   * Contract: a fixed operational horizon $H=14$ days with contract validation (HTTP 422 on an attempt to change the horizon) and optional `planned_promos` support.
   * Inference time: **~55–65 ms** per 14-day horizon with calibrated quantile intervals.

## Quick start

```powershell
# Full run (backtest + training + tests + demo)
.\make.ps1 all

# Run individual tests
py -3.13 -m pytest -v tests

# Offline summary for the interview
py -3.13 scripts/demo_offline.py

# Live forecast via FastAPI
py -3.13 scripts/demo_forecast.py
```

Detailed technical description and result tables: [`REPORT.en.md`](REPORT.en.md).
