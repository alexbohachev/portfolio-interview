"""Завантаження та валідація даних часових рядів попиту."""
from __future__ import annotations

import pandas as pd
from pathlib import Path


REQUIRED_COLUMNS = {
    "date",
    "hub_id",
    "sku_id",
    "demand",
    "unit_price",
    "promo",
    "temperature_c",
    "is_holiday",
}


def load_demand_data(csv_path: str | Path) -> pd.DataFrame:
    path = Path(csv_path)
    if not path.is_file():
        raise FileNotFoundError(f"Файл даних не знайдено: {path}")

    df = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Відсутні обов'язкові колонки у {path}: {missing}")

    df["date"] = pd.to_datetime(df["date"])
    df["demand"] = pd.to_numeric(df["demand"], errors="raise")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="raise")
    df["promo"] = df["promo"].astype(int)
    df["temperature_c"] = pd.to_numeric(df["temperature_c"], errors="raise")
    df["is_holiday"] = df["is_holiday"].astype(int)

    # Сортування для гарантії суворої хронології
    df = df.sort_values(by=["hub_id", "sku_id", "date"]).reset_index(drop=True)
    return df


def validate_continuity(df: pd.DataFrame) -> dict[str, bool]:
    """Перевіряє, що для кожного часового ряду (hub_id, sku_id) немає пропущених календарних днів."""
    status = {}
    grouped = df.groupby(["hub_id", "sku_id"])
    for (hub, sku), group in grouped:
        dates = group["date"].sort_values()
        expected = pd.date_range(start=dates.min(), end=dates.max(), freq="D")
        is_continuous = len(dates) == len(expected) and (dates.values == expected.values).all()
        status[f"{hub}_{sku}"] = bool(is_continuous)
    return status
