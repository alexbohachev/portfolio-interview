"""Тести захисту від витоку цільової змінної та заглядання в майбутнє (Target Leakage Guard)."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from work08.features import create_features


def test_min_lag_must_exceed_or_equal_horizon():
    df = pd.DataFrame({
        "date": pd.date_range("2016-01-01", periods=60),
        "hub_id": "hub_central",
        "sku_id": "SKU_FERT_NPK",
        "demand": 100.0,
        "unit_price": 50.0,
        "promo": 0,
        "temperature_c": 15.0,
        "is_holiday": 0,
    })
    
    # Спроба задати лаг 7 при горизонті 14 повинна викинути помилку
    with pytest.raises(ValueError, match="Target leakage risk"):
        create_features(df, horizon_days=14, lag_steps=[7, 14, 21])


def test_future_demand_tampering_does_not_affect_cutoff_features():
    """Перевірка стійкості до витоку: зміна попиту в майбутньому (t >= T0 - H + 1)
    не повинна змінювати вектори ознак на дату T0.
    """
    n_days = 90
    dates = pd.date_range("2016-01-01", periods=n_days)
    base_demand = np.random.RandomState(42).normal(100, 10, n_days)
    
    df1 = pd.DataFrame({
        "date": dates,
        "hub_id": "hub_central",
        "sku_id": "SKU_FERT_NPK",
        "demand": base_demand,
        "unit_price": 50.0,
        "promo": 0,
        "temperature_c": 15.0,
        "is_holiday": 0,
    })
    
    horizon = 14
    feat1, feature_cols, _ = create_features(df1, horizon_days=horizon)
    
    # Створюємо копію датасету, де останні 13 днів кардинально змінено (наприклад, попит x100)
    df2 = df1.copy()
    cutoff_idx = n_days - horizon # індекс початку майбутнього горизонту
    df2.loc[cutoff_idx + 1:, "demand"] = df2.loc[cutoff_idx + 1:, "demand"] * 100.0
    
    feat2, _, _ = create_features(df2, horizon_days=horizon)
    
    # Рядок на дату T0 (остання дата)
    row1 = feat1[feat1["date"] == dates[-1]][feature_cols].iloc[0]
    row2 = feat2[feat2["date"] == dates[-1]][feature_cols].iloc[0]
    
    # Усі ознаки лагів і ковзних середніх повинні бути ідентичними!
    lag_and_rolling_cols = [c for c in feature_cols if "lag" in c or "rolling" in c]
    for col in lag_and_rolling_cols:
        val1 = row1[col]
        val2 = row2[col]
        assert np.isclose(val1, val2), f"Виявлено витік у колонці {col}: {val1} != {val2}"


def test_rolling_features_isolated_between_series():
    """Перевірка ізоляції між рядами: ковзні вікна на початку ряду B не повинні
    захоплювати хвіст значень ряду A.
    """
    n_days = 60
    dates = pd.date_range("2016-01-01", periods=n_days)
    
    # Ряд A має попит 1000, Ряд B має попит 10
    df_a = pd.DataFrame({
        "date": dates,
        "hub_id": "hub_A",
        "sku_id": "SKU_1",
        "demand": 1000.0,
        "unit_price": 50.0,
        "promo": 0,
        "temperature_c": 15.0,
        "is_holiday": 0,
    })
    df_b = pd.DataFrame({
        "date": dates,
        "hub_id": "hub_B",
        "sku_id": "SKU_2",
        "demand": 10.0,
        "unit_price": 50.0,
        "promo": 0,
        "temperature_c": 15.0,
        "is_holiday": 0,
    })
    
    combined = pd.concat([df_a, df_b], ignore_index=True)
    horizon = 14
    feat_df, feature_cols, _ = create_features(combined, horizon_days=horizon)
    
    # Перевіряємо перші доступні рядки ряду B
    feat_b = feat_df[feat_df["hub_id"] == "hub_B"]
    rolling_cols = [c for c in feature_cols if "rolling_mean" in c]
    
    for col in rolling_cols:
        # Середнє для ряду B повинно бути рівно 10.0, а не сотні від ряду A!
        vals = feat_b[col].values
        assert (vals < 100.0).all(), f"Виявлено перетікання між рядами у {col}: max={vals.max()}"
        assert np.isclose(vals[0], 10.0), f"Перше значення {col} має бути 10.0, отримано {vals[0]}"
