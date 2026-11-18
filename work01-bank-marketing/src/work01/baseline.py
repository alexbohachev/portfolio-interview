from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from work01.data import build_sklearn_preprocessor


def train_baseline(
    x_train: np.ndarray | Any,
    y_train: np.ndarray,
    cfg: dict[str, Any],
    x_frame,
) -> Pipeline:
    pre = build_sklearn_preprocessor(x_frame)
    clf = LogisticRegression(
        max_iter=cfg["baseline"]["max_iter"],
        class_weight=cfg["baseline"]["class_weight"],
        random_state=cfg.get("seed", 42),
        n_jobs=-1,
    )
    pipe = Pipeline([("pre", pre), ("clf", clf)])
    pipe.fit(x_train, y_train)
    return pipe


def predict_proba(pipe: Pipeline, x) -> np.ndarray:
    return pipe.predict_proba(x)[:, 1]