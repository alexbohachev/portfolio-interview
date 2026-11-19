"""Пайплайн виділення ознак із захистом від target leakage (суворе зміщення на горизонт H)."""
from __future__ import annotations

import numpy as np
import pandas as pd


def create_features(
    df: pd.DataFrame,
    horizon_days: int = 14,
    lag_steps: list[int] | None = None,
    rolling_windows: list[int] | None = None,
) -> tuple[pd.DataFrame, list[str], str]:
    """Генерує вектор ознак для прогнозування попиту з горизонтом H днів.

    Захист від витоку цільової змінної (Lookahead / Target Leakage):
    - Усі лаги попиту зміщуються як мінімум на horizon_days (наприклад, t-14, t-21, t-28).
    - Ковзні середні та відхилення рахуються суворо на даних, відомих на момент t - H.
    - Календарні ознаки, планові промоакції та святкові дні відомі заздалегідь для дати t.
    """
    if lag_steps is None:
        lag_steps = [14, 21, 28, 35]
    if rolling_windows is None:
        rolling_windows = [7, 14, 28]

    # Перевірка безпеки від витоку
    min_lag = min(lag_steps)
    if min_lag < horizon_days:
        raise ValueError(
            f"Target leakage risk: мінімальний лаг ({min_lag}) менший за горизонт прогнозування ({horizon_days})."
        )

    df = df.copy()
    df = df.sort_values(by=["hub_id", "sku_id", "date"]).reset_index(drop=True)

    feature_cols: list[str] = []

    # 1. Календарні ознаки (відомі для будь-якої майбутньої дати t)
    df["dow"] = df["date"].dt.dayofweek
    df["day"] = df["date"].dt.day
    df["month"] = df["date"].dt.month
    df["quarter"] = df["date"].dt.quarter
    df["is_weekend"] = (df["dow"] >= 5).astype(int)

    # Циклічні гармонійні ознаки (Fourier sin/cos) для гладкої апроксимації циклів
    df["dow_sin"] = np.sin(2 * np.pi * df["dow"] / 7.0)
    df["dow_cos"] = np.cos(2 * np.pi * df["dow"] / 7.0)
    day_of_year = df["date"].dt.dayofyear
    df["doy_sin"] = np.sin(2 * np.pi * day_of_year / 365.25)
    df["doy_cos"] = np.cos(2 * np.pi * day_of_year / 365.25)

    calendar_features = [
        "dow", "day", "month", "quarter", "is_weekend",
        "dow_sin", "dow_cos", "doy_sin", "doy_cos",
        "promo", "is_holiday", "unit_price", "temperature_c"
    ]
    feature_cols.extend(calendar_features)

    # 2. Категоріальні ідентифікатори серій
    df["hub_cat"] = df["hub_id"].astype("category")
    df["sku_cat"] = df["sku_id"].astype("category")
    feature_cols.extend(["hub_cat", "sku_cat"])

    # 3. Лагові ознаки та ковзні агрегати (суворо згруповані по рядах)
    grouped = df.groupby(["hub_id", "sku_id"])["demand"]

    for lag in lag_steps:
        col_name = f"lag_{lag}"
        df[col_name] = grouped.shift(lag)
        feature_cols.append(col_name)

    # Розрахунок ковзних статистик суворо в межах кожного ряду (hub_id x sku_id)
    # без перетікання значень через межі рядів
    for w in rolling_windows:
        min_p = max(1, w // 2)
        mean_col = f"rolling_mean_{w}_lag{horizon_days}"
        std_col = f"rolling_std_{w}_lag{horizon_days}"

        df[mean_col] = grouped.transform(
            lambda s: s.shift(horizon_days).rolling(window=w, min_periods=min_p).mean()
        )
        df[std_col] = grouped.transform(
            lambda s: s.shift(horizon_days).rolling(window=w, min_periods=min_p).std()
        ).fillna(0.0)

        feature_cols.append(mean_col)
        feature_cols.append(std_col)

    # Дропаємо рядки з початковими NaN через лаги
    max_lag = max(lag_steps) + max(rolling_windows)
    valid_df = df.dropna(subset=feature_cols + ["demand"]).reset_index(drop=True)

    return valid_df, feature_cols, "demand"
