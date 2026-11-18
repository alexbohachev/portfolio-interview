from __future__ import annotations

import pandas as pd

from work04.paths import DATA_RAW

FEATURES = ["hours_used", "maint_score"]
CAT = ["region", "equipment_type"]


def load_events() -> pd.DataFrame:
    path = DATA_RAW / "events.parquet"
    if not path.is_file():
        raise FileNotFoundError(f"Run scripts/seed_data.py — missing {path}")
    return pd.read_parquet(path)


def temporal_split(df: pd.DataFrame, train_ratio: float, val_ratio: float):
    df = df.sort_values("event_time").reset_index(drop=True)
    n = len(df)
    i1 = int(n * train_ratio)
    i2 = int(n * (train_ratio + val_ratio))
    return df.iloc[:i1], df.iloc[i1:i2], df.iloc[i2:]


def matrix(df: pd.DataFrame):
    x_num = df[FEATURES].astype(float)
    x_cat = pd.get_dummies(df[CAT].astype(str), prefix=CAT, dtype=float)
    x = pd.concat([x_num, x_cat], axis=1)
    y = df["target_breakdown_risk"].astype(int).to_numpy()
    return x, y, list(x.columns)


def align_columns(x: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = x.copy()
    for c in columns:
        if c not in out.columns:
            out[c] = 0.0
    return out.reindex(columns=columns, fill_value=0.0)