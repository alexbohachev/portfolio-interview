"""Сегментний аналіз помилок прогнозування (Error Analysis by Segments)."""
from __future__ import annotations

import pandas as pd
from work08.metrics import wape, mae, normalized_bias


def analyze_errors_by_segments(preds_df: pd.DataFrame) -> dict[str, list[dict]]:
    """Розкладає похибки прогнозування LightGBM vs Seasonal Naive по сегментах."""
    
    # 1. Помилки по категоріях товарів (SKU)
    sku_analysis = []
    for sku, grp in preds_df.groupby("sku_id"):
        y_true = grp["demand"].values
        lgb_p = grp["pred_lgb_point"].values
        naive_p = grp["pred_s_naive"].values
        
        sku_analysis.append({
            "segment": "sku",
            "key": sku,
            "sample_count": len(grp),
            "total_demand": round(float(y_true.sum()), 1),
            "lgb_wape": round(wape(y_true, lgb_p), 4),
            "naive_wape": round(wape(y_true, naive_p), 4),
            "lgb_bias": round(normalized_bias(y_true, lgb_p), 4),
            "wape_lift_pct": round((wape(y_true, naive_p) - wape(y_true, lgb_p)) / wape(y_true, naive_p) * 100, 2),
        })

    # 2. Помилки по регіональних хабах
    hub_analysis = []
    for hub, grp in preds_df.groupby("hub_id"):
        y_true = grp["demand"].values
        lgb_p = grp["pred_lgb_point"].values
        naive_p = grp["pred_s_naive"].values
        
        hub_analysis.append({
            "segment": "hub",
            "key": hub,
            "sample_count": len(grp),
            "total_demand": round(float(y_true.sum()), 1),
            "lgb_wape": round(wape(y_true, lgb_p), 4),
            "naive_wape": round(wape(y_true, naive_p), 4),
            "lgb_bias": round(normalized_bias(y_true, lgb_p), 4),
            "wape_lift_pct": round((wape(y_true, naive_p) - wape(y_true, lgb_p)) / wape(y_true, naive_p) * 100, 2),
        })

    # 3. Помилки по промо vs звичайних днях
    promo_analysis = []
    for promo, grp in preds_df.groupby("promo"):
        label = "Promo (Акція)" if promo == 1 else "Non-Promo (Звичайний)"
        y_true = grp["demand"].values
        lgb_p = grp["pred_lgb_point"].values
        naive_p = grp["pred_s_naive"].values
        
        promo_analysis.append({
            "segment": "promo",
            "key": label,
            "sample_count": len(grp),
            "total_demand": round(float(y_true.sum()), 1),
            "lgb_wape": round(wape(y_true, lgb_p), 4),
            "naive_wape": round(wape(y_true, naive_p), 4),
            "lgb_bias": round(normalized_bias(y_true, lgb_p), 4),
            "wape_lift_pct": round((wape(y_true, naive_p) - wape(y_true, lgb_p)) / wape(y_true, naive_p) * 100, 2),
        })

    # 4. Помилки будні vs вихідні
    day_type_analysis = []
    for is_wk, grp in preds_df.groupby("is_weekend"):
        label = "Weekend (Вихідні)" if is_wk == 1 else "Weekday (Будні)"
        y_true = grp["demand"].values
        lgb_p = grp["pred_lgb_point"].values
        naive_p = grp["pred_s_naive"].values
        
        day_type_analysis.append({
            "segment": "day_type",
            "key": label,
            "sample_count": len(grp),
            "total_demand": round(float(y_true.sum()), 1),
            "lgb_wape": round(wape(y_true, lgb_p), 4),
            "naive_wape": round(wape(y_true, naive_p), 4),
            "lgb_bias": round(normalized_bias(y_true, lgb_p), 4),
            "wape_lift_pct": round((wape(y_true, naive_p) - wape(y_true, lgb_p)) / wape(y_true, naive_p) * 100, 2),
        })

    return {
        "by_sku": sku_analysis,
        "by_hub": hub_analysis,
        "by_promo": promo_analysis,
        "by_day_type": day_type_analysis,
    }
