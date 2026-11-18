from __future__ import annotations

import hashlib
import io
import zipfile
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import requests
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def download_bank_zip(url: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        return dest
    resp = requests.get(url, timeout=120)
    resp.raise_for_status()
    dest.write_bytes(resp.content)
    return dest


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_bank_csv(zip_path: Path, csv_name: str, sep: str) -> pd.DataFrame:
    with zipfile.ZipFile(zip_path) as zf:
        with zf.open(csv_name) as raw:
            return pd.read_csv(raw, sep=sep)


def temporal_splits(
    n_rows: int,
    train_end: int,
    val_end: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    train_idx = np.arange(0, train_end)
    val_idx = np.arange(train_end, val_end)
    test_idx = np.arange(val_end, n_rows)
    return train_idx, val_idx, test_idx


def prepare_features_target(
    df: pd.DataFrame,
    target: str,
    drop_columns: list[str],
) -> tuple[pd.DataFrame, np.ndarray]:
    work = df.drop(columns=drop_columns, errors="ignore")
    y = (work[target] == "yes").astype(np.int64).to_numpy()
    x = work.drop(columns=[target])
    return x, y


def build_sklearn_preprocessor(x: pd.DataFrame) -> ColumnTransformer:
    cat_cols = x.select_dtypes(include=["object"]).columns.tolist()
    num_cols = [c for c in x.columns if c not in cat_cols]
    return ColumnTransformer(
        transformers=[
            ("num", Pipeline([("scaler", StandardScaler())]), num_cols),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                cat_cols,
            ),
        ],
        verbose_feature_names_out=False,
    )


def load_dataset(cfg: dict[str, Any], raw_dir: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    zip_path = raw_dir / "bank.zip"
    download_bank_zip(cfg["data"]["url"], zip_path)
    meta = {"zip_sha256": sha256_file(zip_path), "zip_path": str(zip_path)}
    with zipfile.ZipFile(zip_path) as zf:
        csv_bytes = zf.read(cfg["data"]["csv_name"])
    csv_digest = hashlib.sha256(csv_bytes).hexdigest()
    meta["csv_sha256"] = csv_digest
    expected = cfg["data"].get("csv_sha256")
    if expected and csv_digest != expected:
        raise ValueError(
            f"SHA-256 bank-full.csv mismatch: got {csv_digest}, expected {expected}. "
            "Перевірте, що використовується bank-full.csv з bank.zip (не bank-additional)."
        )
    df = pd.read_csv(io.BytesIO(csv_bytes), sep=cfg["data"]["sep"])
    if len(df) != cfg["data"]["split"]["total_rows"]:
        raise ValueError(f"Очікувалось {cfg['data']['split']['total_rows']} рядків, отримано {len(df)}")
    meta["n_rows"] = len(df)
    return df, meta


def split_indices(cfg: dict[str, Any], n_rows: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    sp = cfg["data"]["split"]
    return temporal_splits(n_rows, sp["train_end"], sp["val_end"])