from __future__ import annotations

import numpy as np


def expected_cost(y: np.ndarray, prob: np.ndarray, threshold: float, costs: dict) -> float:
    pred = (prob >= threshold).astype(int)
    fp = int(((pred == 1) & (y == 0)).sum())
    fn = int(((pred == 0) & (y == 1)).sum())
    reviews = int(pred.sum())
    n = len(y)
    return (fp * costs["false_positive"] + fn * costs["false_negative"] + reviews * costs["human_review"]) / n


def tune_threshold_cost(y: np.ndarray, prob: np.ndarray, costs: dict) -> tuple[float, float]:
    grid = np.linspace(0.05, 0.95, 37)
    best_t = 0.5
    best_c = float("inf")
    for t in grid:
        c = expected_cost(y, prob, float(t), costs)
        if c < best_c:
            best_c = c
            best_t = float(t)
    return best_t, best_c