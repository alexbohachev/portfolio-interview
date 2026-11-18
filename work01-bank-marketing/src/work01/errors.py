from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def _bucket(row: pd.Series, y_true: int, y_pred: int, prob: float) -> str:
    if y_true == 1 and y_pred == 0:
        if prob < 0.25:
            return "FN_low_score"
        if prob >= 0.45:
            return "FN_borderline_high"
        return "FN_mid_score"
    if y_true == 0 and y_pred == 1:
        if prob > 0.75:
            return "FP_high_confidence"
        return "FP_borderline"
    if y_true == 1 and y_pred == 1 and prob < 0.55:
        return "TP_hard_correct"
    if y_true == 0 and y_pred == 0 and prob > 0.45:
        return "TN_hard_correct"
    return "other_correct"


def build_error_analysis(
    x_test: pd.DataFrame,
    y_test: np.ndarray,
    prob: np.ndarray,
    threshold: float,
    max_cases: int = 20,
) -> dict[str, Any]:
    y_pred = (prob >= threshold).astype(np.int64)
    wrong = np.where(y_pred != y_test)[0]
    correct = np.where(y_pred == y_test)[0]

    records: list[dict[str, Any]] = []
    for i in wrong:
        records.append(
            {
                "test_index": int(i),
                "row_1based": int(38430 + i),
                "y_true": int(y_test[i]),
                "y_pred": int(y_pred[i]),
                "prob_yes": round(float(prob[i]), 4),
                "bucket": _bucket(x_test.iloc[i], int(y_test[i]), int(y_pred[i]), float(prob[i])),
                "age": int(x_test.iloc[i].get("age", -1)) if "age" in x_test.columns else None,
                "month": str(x_test.iloc[i].get("month", "")) if "month" in x_test.columns else None,
            }
        )

    # складні правильні: TP з низькою ймовірністю, TN з високою
    hard_correct_idx = []
    for i in correct:
        b = _bucket(x_test.iloc[i], int(y_test[i]), int(y_pred[i]), float(prob[i]))
        if b in ("TP_hard_correct", "TN_hard_correct"):
            hard_correct_idx.append(i)

    by_bucket: dict[str, list[dict[str, Any]]] = {}
    for r in records:
        by_bucket.setdefault(r["bucket"], []).append(r)
    for items in by_bucket.values():
        items.sort(key=lambda r: abs(r["prob_yes"] - threshold), reverse=True)

    selected: list[dict[str, Any]] = []
    bucket_order = sorted(by_bucket.keys(), key=lambda b: -len(by_bucket[b]))
    while len(selected) < max_cases and bucket_order:
        progressed = False
        for b in bucket_order:
            pool = by_bucket.get(b, [])
            if pool:
                selected.append(pool.pop(0))
                progressed = True
                if len(selected) >= max_cases:
                    break
        if not progressed:
            break

    remaining = max_cases - len(selected)
    if remaining > 0:
        for i in hard_correct_idx[:remaining]:
            selected.append(
                {
                    "test_index": int(i),
                    "row_1based": int(38430 + i),
                    "y_true": int(y_test[i]),
                    "y_pred": int(y_pred[i]),
                    "prob_yes": round(float(prob[i]), 4),
                    "bucket": _bucket(x_test.iloc[i], int(y_test[i]), int(y_pred[i]), float(prob[i])),
                    "age": int(x_test.iloc[i].get("age", -1)) if "age" in x_test.columns else None,
                    "month": str(x_test.iloc[i].get("month", "")) if "month" in x_test.columns else None,
                }
            )

    buckets: dict[str, int] = {}
    for r in records:
        buckets[r["bucket"]] = buckets.get(r["bucket"], 0) + 1

    return {
        "n_errors": int(len(wrong)),
        "n_test": int(len(y_test)),
        "error_rate": round(len(wrong) / len(y_test), 4),
        "bucket_counts_errors_only": buckets,
        "cases": selected,
        "threshold": threshold,
    }