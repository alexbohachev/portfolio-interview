from __future__ import annotations

import numpy as np
from sklearn.metrics import f1_score


def tune_threshold_macro_f1(y_true: np.ndarray, y_prob: np.ndarray, grid: np.ndarray | None = None) -> tuple[float, float]:
    if grid is None:
        grid = np.linspace(0.05, 0.95, 91)
    best_t = 0.5
    best_f1 = -1.0
    for t in grid:
        pred = (y_prob >= t).astype(np.int64)
        f1 = f1_score(y_true, pred, average="macro", zero_division=0)
        if f1 > best_f1:
            best_f1 = float(f1)
            best_t = float(t)
    return best_t, best_f1