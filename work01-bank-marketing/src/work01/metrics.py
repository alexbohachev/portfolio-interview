from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.metrics import average_precision_score, f1_score


def brier_score(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    y_true = y_true.astype(np.float64)
    return float(np.mean((y_prob - y_true) ** 2))


def classification_scores(y_true: np.ndarray, y_prob: np.ndarray, threshold: float = 0.5) -> dict[str, float]:
    y_pred = (y_prob >= threshold).astype(np.int64)
    return {
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "brier": brier_score(y_true, y_prob),
        "pr_auc": float(average_precision_score(y_true, y_prob)),
    }


@dataclass
class BootstrapCI:
    low: float
    high: float
    point: float


def bootstrap_metric_diff(
    y_true: np.ndarray,
    prob_baseline: np.ndarray,
    prob_candidate: np.ndarray,
    metric_fn,
    n_resamples: int = 1000,
    ci: float = 0.95,
    seed: int = 0,
) -> BootstrapCI:
    rng = np.random.default_rng(seed)
    n = len(y_true)
    diffs = []
    for _ in range(n_resamples):
        idx = rng.integers(0, n, size=n)
        m_base = metric_fn(y_true[idx], prob_baseline[idx])
        m_cand = metric_fn(y_true[idx], prob_candidate[idx])
        diffs.append(m_cand - m_base)
    diffs_arr = np.asarray(diffs, dtype=np.float64)
    alpha = (1 - ci) / 2
    return BootstrapCI(
        point=float(np.mean(diffs_arr)),
        low=float(np.quantile(diffs_arr, alpha)),
        high=float(np.quantile(diffs_arr, 1 - alpha)),
    )


def prob_for_metrics(proba: np.ndarray | None, y_score: np.ndarray | None, y_pred: np.ndarray) -> np.ndarray:
    if proba is not None:
        return proba[:, 1] if proba.ndim == 2 else proba
    if y_score is not None:
        return 1.0 / (1.0 + np.exp(-y_score))
    return y_pred.astype(np.float64)