"""Хронологічний ковзний бектестинг (Rolling-Window Chronological Backtesting) без витоку даних."""
from __future__ import annotations

import pandas as pd
from typing import Any
from work08.baselines import SeasonalNaiveForecaster, HistoricalDowMovingAverageForecaster
from work08.features import create_features
from work08.metrics import evaluate_forecasts, coverage_rate, pinball_loss
from work08.models import LightGBMPointForecaster, LightGBMQuantileForecaster


def run_rolling_backtest(
    df: pd.DataFrame,
    horizon_days: int = 14,
    n_folds: int = 4,
    c_under: float = 5.0,
    c_over: float = 1.0,
) -> dict[str, Any]:
    """Виконує строгий хронологічний expanding-window бектестинг на n_folds фолдах."""
    feat_df, feature_cols, target_col = create_features(df, horizon_days=horizon_days)
    
    unique_dates = sorted(feat_df["date"].unique())
    total_dates = len(unique_dates)
    total_test_days = horizon_days * n_folds
    
    if total_dates < total_test_days + 60:
        raise ValueError("Недостатньо історичних дат для проведення надійного бектестингу.")

    fold_results = []
    all_predictions = []

    for fold_idx in range(n_folds):
        # Розрахунок меж для fold_idx (відлік з кінця історії)
        # fold 0: найбільш ранній з тестових фолдів, fold n-1: найсвіжіший
        test_offset_start = total_test_days - (fold_idx * horizon_days)
        test_offset_end = test_offset_start - horizon_days
        
        test_start_date = unique_dates[-test_offset_start]
        test_end_date = unique_dates[-test_offset_end - 1]
        
        train_mask = feat_df["date"] < test_start_date
        test_mask = (feat_df["date"] >= test_start_date) & (feat_df["date"] <= test_end_date)
        
        train_fold = feat_df[train_mask].copy()
        test_fold = feat_df[test_mask].copy()
        
        y_test = test_fold[target_col].values
        
        # 1. Baseline 1: Seasonal Naive
        s_naive = SeasonalNaiveForecaster(season_length=7).fit(train_fold)
        pred_s_naive = s_naive.predict(test_fold)
        metrics_s_naive = evaluate_forecasts(y_test, pred_s_naive, c_under, c_over)
        
        # 2. Baseline 2: Historical DOW MA
        dow_ma = HistoricalDowMovingAverageForecaster(n_weeks=4).fit(train_fold)
        pred_dow_ma = dow_ma.predict(test_fold)
        metrics_dow_ma = evaluate_forecasts(y_test, pred_dow_ma, c_under, c_over)
        
        # 3. Model: LightGBM Point Forecaster
        # Останні 14 днів навчальної вибірки беремо як early-stopping val set
        train_dates = sorted(train_fold["date"].unique())
        val_start_date = train_dates[-horizon_days]
        val_submask = train_fold["date"] >= val_start_date
        
        sub_train = train_fold[~val_submask]
        sub_val = train_fold[val_submask]
        
        lgb_point = LightGBMPointForecaster()
        lgb_point.fit(
            sub_train,
            sub_train[target_col].values,
            feature_cols,
            val_set=(sub_val, sub_val[target_col].values),
        )
        pred_lgb_point = lgb_point.predict(test_fold)
        metrics_lgb_point = evaluate_forecasts(y_test, pred_lgb_point, c_under, c_over)
        
        # 4. Model: LightGBM Quantile Forecaster
        crit_ratio = c_under / (c_under + c_over)
        lgb_quantile = LightGBMQuantileForecaster(
            quantiles=[0.10, 0.50, 0.90],
            critical_ratio=crit_ratio,
        )
        lgb_quantile.fit(train_fold, train_fold[target_col].values, feature_cols)
        preds_q = lgb_quantile.predict(test_fold)
        pred_p10 = preds_q[0.10]
        pred_p50 = preds_q[0.50]
        pred_p90 = preds_q[0.90]
        pred_safety = lgb_quantile.predict_safety_stock(test_fold)
        
        metrics_lgb_safety = evaluate_forecasts(y_test, pred_safety, c_under, c_over)
        cov_80 = round(coverage_rate(y_test, pred_p10, pred_p90), 4)
        
        fold_summary = {
            "fold": fold_idx + 1,
            "train_end": str(train_dates[-1].strftime("%Y-%m-%d")),
            "test_start": str(test_start_date.strftime("%Y-%m-%d")),
            "test_end": str(test_end_date.strftime("%Y-%m-%d")),
            "n_test_samples": len(test_fold),
            "baseline_seasonal_naive": metrics_s_naive,
            "baseline_dow_ma": metrics_dow_ma,
            "lightgbm_point": metrics_lgb_point,
            "lightgbm_safety_stock": metrics_lgb_safety,
            "quantile_coverage_80": cov_80,
            "pinball_loss_p50": round(pinball_loss(y_test, pred_p50, 0.50), 3),
        }
        fold_results.append(fold_summary)
        
        # Збереження детальних прогнозів для сегментного аналізу
        test_fold_copy = test_fold.copy()
        test_fold_copy["fold"] = fold_idx + 1
        test_fold_copy["pred_s_naive"] = pred_s_naive
        test_fold_copy["pred_dow_ma"] = pred_dow_ma
        test_fold_copy["pred_lgb_point"] = pred_lgb_point
        test_fold_copy["pred_safety_stock"] = pred_safety
        test_fold_copy["pred_p10"] = pred_p10
        test_fold_copy["pred_p90"] = pred_p90
        all_predictions.append(test_fold_copy)

    # Агрегація середніх метрик за всіма фолдами
    combined_preds = pd.concat(all_predictions, ignore_index=True)
    
    avg_s_naive = {
        "wape": round(float(combined_preds.apply(lambda _: 0, axis=1).mean() or 0), 4),
        "mean_fold_wape": round(float(pd.Series([f["baseline_seasonal_naive"]["wape"] for f in fold_results]).mean()), 4),
        "mean_fold_cost": round(float(pd.Series([f["baseline_seasonal_naive"]["inventory_cost"] for f in fold_results]).mean()), 1),
    }
    avg_lgb = {
        "mean_fold_wape": round(float(pd.Series([f["lightgbm_point"]["wape"] for f in fold_results]).mean()), 4),
        "mean_fold_cost": round(float(pd.Series([f["lightgbm_point"]["inventory_cost"] for f in fold_results]).mean()), 1),
    }
    avg_safety = {
        "mean_fold_cost": round(float(pd.Series([f["lightgbm_safety_stock"]["inventory_cost"] for f in fold_results]).mean()), 1),
    }

    # Розрахунок відносного зниження WAPE та скорочення витрат на дефіцит/надлишок
    wape_reduction_pct = round(
        (avg_s_naive["mean_fold_wape"] - avg_lgb["mean_fold_wape"]) / avg_s_naive["mean_fold_wape"] * 100, 2
    )
    cost_reduction_pct = round(
        (avg_s_naive["mean_fold_cost"] - avg_safety["mean_fold_cost"]) / avg_s_naive["mean_fold_cost"] * 100, 2
    )

    return {
        "horizon_days": horizon_days,
        "n_folds": n_folds,
        "c_under": c_under,
        "c_over": c_over,
        "folds": fold_results,
        "summary": {
            "seasonal_naive_wape": avg_s_naive["mean_fold_wape"],
            "lightgbm_wape": avg_lgb["mean_fold_wape"],
            "wape_reduction_pct": wape_reduction_pct,
            "seasonal_naive_cost": avg_s_naive["mean_fold_cost"],
            "lightgbm_safety_cost": avg_safety["mean_fold_cost"],
            "cost_reduction_pct": cost_reduction_pct,
        },
        "combined_predictions": combined_preds,
        "feature_cols": feature_cols,
    }
