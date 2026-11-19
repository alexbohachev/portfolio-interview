"""Пайплайн виділення ознак із захистом від target leakage (суворе зміщення на горизонт H)."""
from __future__ import annotations

import numpy as np
import pandas as pd


def compute_seasonal_temperature(day_of_year: int | np.ndarray) -> float | np.ndarray:
    """Детермінована сезонна очікувана температура для екзогенного прогнозу без випадкового шуму."""
    doy = np.asarray(day_of_year)
    temp = 10.0 + 15.0 * np.sin(2 * np.pi * (doy - 100) / 365.25)
    res = np.round(temp, 1)
    if res.ndim == 0:
        return float(res)
    return res


def is_calendar_holiday(month: int, day: int) -> int:
    """Визначення святкових днів календаря (новий рік, різдво, травневі)."""
    return 1 if (month == 1 and day in (1, 7)) or (month == 5 and day in (1, 9)) else 0


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


def build_ex_ante_features(
    history_df: pd.DataFrame,
    cutoff_date: pd.Timestamp | str | None = None,
    horizon_days: int = 14,
    series_subset: tuple[str, str] | None = None,
    planned_promos: dict[tuple[str, str], list[int]] | list[int] | None = None,
) -> tuple[pd.DataFrame, list[str]]:
    """Формує вектори ознак для майбутнього горизонту H днів строго на інформації,
    доступній на момент відсікання cutoff_date (Ex-Ante Feature Engineering).

    Забезпечує 100% уніфікацію між бектестингом та продакшн-сервінгом (нульовий skew):
    - unit_price: остання відома ціна на момент cutoff_date (persistence)
    - temperature_c: очікувана сезонна синусоїдальна температура (forecasted seasonal proxy)
    - promo: плановий графік промоакцій (або 0 за замовчуванням)
    - is_holiday: відомі календарні дати свят
    - лаги та ковзні середні: розраховуються строго на історії спостережень <= cutoff_date
    """
    if series_subset is not None:
        history_df = history_df[
            (history_df["hub_id"] == series_subset[0]) & (history_df["sku_id"] == series_subset[1])
        ].copy()

    if cutoff_date is None:
        cutoff_dt = pd.to_datetime(history_df["date"].max())
    else:
        cutoff_dt = pd.to_datetime(cutoff_date)

    # Залишаємо історію строго до моменту відсікання
    history_df = history_df[pd.to_datetime(history_df["date"]) <= cutoff_dt].copy()
    history_df["date"] = pd.to_datetime(history_df["date"])

    future_dates = pd.date_range(start=cutoff_dt + pd.Timedelta(days=1), periods=horizon_days, freq="D")
    future_rows = []

    grouped = history_df.groupby(["hub_id", "sku_id"])
    for (hub, sku), grp in grouped:
        sorted_grp = grp.sort_values(by="date")
        last_price = float(sorted_grp.iloc[-1]["unit_price"])

        # Визначаємо промо-масив для цієї серії
        if isinstance(planned_promos, list):
            series_promos = planned_promos
        elif isinstance(planned_promos, dict):
            series_promos = planned_promos.get((hub, sku), [0] * horizon_days)
        else:
            series_promos = [0] * horizon_days

        for day_idx, f_dt in enumerate(future_dates):
            doy = f_dt.timetuple().tm_yday
            avg_temp = compute_seasonal_temperature(doy)
            is_hol = is_calendar_holiday(f_dt.month, f_dt.day)
            promo_val = int(series_promos[day_idx]) if day_idx < len(series_promos) else 0

            future_rows.append({
                "date": f_dt,
                "hub_id": hub,
                "sku_id": sku,
                "demand": 0.0,  # плейсхолдер для shift >= H
                "unit_price": last_price,
                "promo": promo_val,
                "temperature_c": avg_temp,
                "is_holiday": is_hol,
            })

    extended_df = pd.concat([history_df, pd.DataFrame(future_rows)], ignore_index=True)
    extended_feat, feat_cols, _ = create_features(extended_df, horizon_days=horizon_days)

    inference_df = (
        extended_feat[extended_feat["date"].isin(future_dates)]
        .sort_values(by=["hub_id", "sku_id", "date"])
        .reset_index(drop=True)
    )

    return inference_df, feat_cols

