"""Хронологічний ковзний бектестинг (Rolling-Window Chronological Backtesting) з повною ексанте ізоляцією.

Усуває Train-Serving / Backtest-Inference Skew:
Для кожного тестового фолду ознаки майбутнього горизонту генеруються функцією `build_ex_ante_features`,
що відтворює рівно ту інформацію, яка доступна API сервінгу на момент cutoff:
- unit_price: остання відома ціна до дати прогнозу (persistence)
- temperature_c: кліматологічна сезонна гармоніка (детермінований прогноз без стохастичного шуму)
- promo: плановий графік промоакцій (0 за замовчуванням за відсутності затверджених кампаній)
- is_holiday: відомі календарні свята
- лаги та ковзні агрегати: розраховуються строго на історії <= cutoff_date
"""
from __future__ import annotations

from typing import Any
import pandas as pd

from work08.baselines import HistoricalDowMovingAverageForecaster, SeasonalNaiveForecaster
from work08.features import build_ex_ante_features, create_features
from work08.metrics import coverage_rate, evaluate_forecasts, pinball_loss
from work08.models import LightGBMPointForecaster, LightGBMQuantileForecaster

# 4 репрезентативні агро-сезони року 2017:
# 1. Весняна посівна кампанія (пік насіння та добрив)
# 2. Літній вегетаційний догляд (пік ЗЗР/гербіцидів)
# 3. Осіння кампанія та збір (другий сплеск озимих культур)
# 4. Зимове міжсезоння (базовий попит та запчастини ТО)
DEFAULT_SEASONAL_FOLDS = [
    {"season": "Spring Sowing Peak", "cutoff": "2017-04-15"},
    {"season": "Summer Crop Protection", "cutoff": "2017-07-15"},
    {"season": "Autumn Harvest & Sowing", "cutoff": "2017-10-01"},
    {"season": "Winter Baseline", "cutoff": "2017-12-15"},
]


def run_rolling_backtest(
    df: pd.DataFrame,
    horizon_days: int = 14,
    n_folds: int = 4,
    c_under: float = 5.0,
    c_over: float = 1.0,
    use_seasonal_slices: bool = True,
    custom_folds: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Виконує строгий хронологічний expanding-window бектестинг з ex-ante конструюванням ознак."""
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])

    # Визначаємо конфігурацію фолдів
    if custom_folds is not None:
        fold_configs = custom_folds
    elif use_seasonal_slices and n_folds == len(DEFAULT_SEASONAL_FOLDS):
        fold_configs = DEFAULT_SEASONAL_FOLDS
    else:
        # Fallback на рівномірне розбиття з кінця історії
        unique_dates = sorted(df["date"].unique())
        total_test_days = horizon_days * n_folds
        if len(unique_dates) < total_test_days + 60:
            raise ValueError("Недостатньо історичних дат для проведення надійного бектестингу.")
        fold_configs = []
        for fold_idx in range(n_folds):
            test_offset_start = total_test_days - (fold_idx * horizon_days)
            cutoff_dt = unique_dates[-test_offset_start - 1]
            fold_configs.append({
                "season": f"Window {fold_idx + 1}",
                "cutoff": str(cutoff_dt.strftime("%Y-%m-%d")),
            })

    fold_results = []
    all_predictions = []
    feature_cols_cached: list[str] = []

    for fold_idx, fold_cfg in enumerate(fold_configs):
        cutoff_dt = pd.to_datetime(fold_cfg["cutoff"])
        season_name = fold_cfg["season"]

        # 1. Історія спостережень строго до cutoff_dt
        history_df = df[df["date"] <= cutoff_dt].copy()

        # 2. Фактичні спостереження майбутнього горизонту H днів для валідації
        future_start_dt = cutoff_dt + pd.Timedelta(days=1)
        future_end_dt = cutoff_dt + pd.Timedelta(days=horizon_days)
        actual_test_df = (
            df[(df["date"] >= future_start_dt) & (df["date"] <= future_end_dt)]
            .sort_values(by=["hub_id", "sku_id", "date"])
            .reset_index(drop=True)
        )

        if len(actual_test_df) == 0:
            raise ValueError(f"Тестовий горизонт для cutoff={cutoff_dt} виходить за межі доступного датасету.")

        # 3. Навчальні ознаки на історії (без витоку даних)
        train_feat, feature_cols, target_col = create_features(history_df, horizon_days=horizon_days)
        feature_cols_cached = feature_cols

        # 4. Ex-Ante вектори ознак для тестового періоду (ідентично сервінгу в API)
        test_feat, _ = build_ex_ante_features(
            history_df=history_df,
            cutoff_date=cutoff_dt,
            horizon_days=horizon_days,
            series_subset=None,
            planned_promos=None,  # стандартна operational policy: без припущення про несподівані акції
        )

        y_test = actual_test_df[target_col].values

        # 5. Бейзлайн 1: Seasonal Naive
        s_naive = SeasonalNaiveForecaster(season_length=7).fit(train_feat)
        pred_s_naive = s_naive.predict(test_feat)
        metrics_s_naive = evaluate_forecasts(y_test, pred_s_naive, c_under, c_over)

        # 6. Бейзлайн 2: Historical DOW MA
        dow_ma = HistoricalDowMovingAverageForecaster(n_weeks=4).fit(train_feat)
        pred_dow_ma = dow_ma.predict(test_feat)
        metrics_dow_ma = evaluate_forecasts(y_test, pred_dow_ma, c_under, c_over)

        # 7. Точкова модель: LightGBM Point Forecaster
        train_dates = sorted(train_feat["date"].unique())
        val_days = min(56, max(horizon_days, len(train_dates) // 4))
        val_start_date = train_dates[-val_days]
        val_submask = train_feat["date"] >= val_start_date

        sub_train = train_feat[~val_submask]
        sub_val = train_feat[val_submask]

        lgb_point = LightGBMPointForecaster()
        lgb_point.fit(
            sub_train,
            sub_train[target_col].values,
            feature_cols,
            val_set=(sub_val, sub_val[target_col].values),
        )
        pred_lgb_point = lgb_point.predict(test_feat)
        metrics_lgb_point = evaluate_forecasts(y_test, pred_lgb_point, c_under, c_over)

        # 8. Квантильна модель: LightGBM Quantile Forecaster з конформним калібруванням (CQR)
        crit_ratio = c_under / (c_under + c_over)
        lgb_quantile = LightGBMQuantileForecaster(
            quantiles=[0.10, 0.50, 0.90],
            critical_ratio=crit_ratio,
            conformal_target=0.85,
        )
        lgb_quantile.fit(
            sub_train,
            sub_train[target_col].values,
            feature_cols,
            val_set=(sub_val, sub_val[target_col].values),
        )
        preds_q_raw = lgb_quantile.predict(test_feat, calibrated=False)
        pred_p10_raw = preds_q_raw[0.10]
        pred_p50 = preds_q_raw[0.50]
        pred_p90_raw = preds_q_raw[0.90]

        preds_q_cal = lgb_quantile.predict(test_feat, calibrated=True)
        pred_p10_cal = preds_q_cal[0.10]
        pred_p90_cal = preds_q_cal[0.90]

        pred_safety = lgb_quantile.predict_safety_stock(test_feat)
        metrics_lgb_safety = evaluate_forecasts(y_test, pred_safety, c_under, c_over)

        cov_80_raw = round(coverage_rate(y_test, pred_p10_raw, pred_p90_raw), 4)
        cov_80_cal = round(coverage_rate(y_test, pred_p10_cal, pred_p90_cal), 4)
        q_conf_adj = round(lgb_quantile.conformal_adjustment_80_, 2)

        fold_summary = {
            "fold": fold_idx + 1,
            "season": season_name,
            "cutoff_date": str(cutoff_dt.strftime("%Y-%m-%d")),
            "train_end": str(train_dates[-1].strftime("%Y-%m-%d")),
            "test_start": str(future_start_dt.strftime("%Y-%m-%d")),
            "test_end": str(future_end_dt.strftime("%Y-%m-%d")),
            "n_test_samples": len(actual_test_df),
            "baseline_seasonal_naive": metrics_s_naive,
            "baseline_dow_ma": metrics_dow_ma,
            "lightgbm_point": metrics_lgb_point,
            "lightgbm_safety_stock": metrics_lgb_safety,
            "quantile_coverage_80": cov_80_raw,
            "raw_quantile_coverage_80": cov_80_raw,
            "calibrated_quantile_coverage_80": cov_80_cal,
            "conformal_adjustment_demand_units": q_conf_adj,
            "pinball_loss_p50": round(pinball_loss(y_test, pred_p50, 0.50), 3),
        }
        fold_results.append(fold_summary)

        # Збереження прогнозів для сегментного аналізу
        test_pred_df = actual_test_df.copy()
        test_pred_df["fold"] = fold_idx + 1
        test_pred_df["season"] = season_name
        test_pred_df["is_weekend"] = (test_pred_df["date"].dt.dayofweek >= 5).astype(int)
        test_pred_df["pred_s_naive"] = pred_s_naive
        test_pred_df["pred_dow_ma"] = pred_dow_ma
        test_pred_df["pred_lgb_point"] = pred_lgb_point
        test_pred_df["pred_safety_stock"] = pred_safety
        test_pred_df["pred_p10"] = pred_p10_raw
        test_pred_df["pred_p90"] = pred_p90_raw
        test_pred_df["pred_p10_raw"] = pred_p10_raw
        test_pred_df["pred_p90_raw"] = pred_p90_raw
        test_pred_df["pred_p10_calibrated"] = pred_p10_cal
        test_pred_df["pred_p90_calibrated"] = pred_p90_cal
        test_pred_df["ex_ante_temperature_c"] = test_feat["temperature_c"].values
        test_pred_df["ex_ante_unit_price"] = test_feat["unit_price"].values
        test_pred_df["ex_ante_promo"] = test_feat["promo"].values
        all_predictions.append(test_pred_df)

    combined_preds = pd.concat(all_predictions, ignore_index=True)

    avg_s_naive = {
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
            "mean_raw_coverage_80": round(float(pd.Series([f["raw_quantile_coverage_80"] for f in fold_results]).mean()), 4),
            "mean_calibrated_coverage_80": round(float(pd.Series([f["calibrated_quantile_coverage_80"] for f in fold_results]).mean()), 4),
        },
        "combined_predictions": combined_preds,
        "feature_cols": feature_cols_cached,
    }
