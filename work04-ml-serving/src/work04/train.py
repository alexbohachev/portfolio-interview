from __future__ import annotations

import json
from pathlib import Path

import joblib
import lightgbm as lgb
import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss

from work04.data import align_columns, load_events, matrix, temporal_split
from work04.threshold import tune_threshold_cost
from work04.paths import ARTIFACTS


def _metrics(y: np.ndarray, prob: np.ndarray) -> dict:
    return {
        "pr_auc": float(average_precision_score(y, prob)),
        "brier": float(brier_score_loss(y, prob)),
        "positive_rate": float(y.mean()),
    }


def train_all(cfg: dict) -> dict:
    df = load_events()
    train, val, test = temporal_split(df, cfg["data"]["train_ratio"], cfg["data"]["val_ratio"])
    x_train, y_train, cols = matrix(train)
    x_val, y_val, _ = matrix(val)
    x_test, y_test, _ = matrix(test)
    x_val = align_columns(x_val, cols)
    x_test = align_columns(x_test, cols)

    baseline = LogisticRegression(max_iter=500, class_weight="balanced")
    baseline.fit(x_train, y_train)
    p_val_b = baseline.predict_proba(x_val)[:, 1]
    p_test_b = baseline.predict_proba(x_test)[:, 1]

    lgbm = lgb.LGBMClassifier(
        n_estimators=120,
        learning_rate=0.05,
        num_leaves=31,
        class_weight="balanced",
        random_state=cfg["seed"],
        verbosity=-1,
    )
    candidate = CalibratedClassifierCV(lgbm, method=cfg["model"]["calibration"], cv=3)
    candidate.fit(x_train, y_train)
    p_val_c = candidate.predict_proba(x_val)[:, 1]
    p_test_c = candidate.predict_proba(x_test)[:, 1]

    costs = cfg["costs"]
    t_b, cost_b = tune_threshold_cost(y_val, p_val_b, costs)
    t_c, cost_c = tune_threshold_cost(y_val, p_val_c, costs)

    bundle = {
        "model_version": "work04-v1.0",
        "preprocessing_version": "cols-v1",
        "schema_version": 1,
        "feature_columns": cols,
        "threshold_baseline": t_b,
        "threshold_candidate": t_c,
        "baseline": baseline,
        "candidate": candidate,
    }
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, ARTIFACTS / "model_bundle.joblib")
    meta = {
        "model_version": bundle["model_version"],
        "preprocessing_version": bundle["preprocessing_version"],
        "baseline_test": _metrics(y_test, p_test_b),
        "candidate_test": _metrics(y_test, p_test_c),
        "expected_cost_val_baseline": cost_b,
        "expected_cost_val_candidate": cost_c,
        "threshold_baseline": t_b,
        "threshold_candidate": t_c,
    }
    (ARTIFACTS / "train_metrics.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return meta