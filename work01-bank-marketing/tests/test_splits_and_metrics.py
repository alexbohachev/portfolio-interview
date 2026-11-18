import numpy as np
import pandas as pd
import pytest

from work01.config import load_config
from work01.data import prepare_features_target, split_indices
from work01.metrics import brier_score, classification_scores
from work01.paths import CONFIG_PATH


def test_temporal_split_sizes():
    cfg = load_config(CONFIG_PATH)
    n = cfg["data"]["split"]["total_rows"]
    train_idx, val_idx, test_idx = split_indices(cfg, n)
    assert len(train_idx) == 31647
    assert len(val_idx) == 6782
    assert len(test_idx) == 6782
    assert len(train_idx) + len(val_idx) + len(test_idx) == n


def test_duration_dropped():
    cfg = load_config(CONFIG_PATH)
    df = pd.DataFrame(
        {
            "age": [30],
            "job": ["admin."],
            "duration": [100],
            "y": ["no"],
        }
    )
    x, y = prepare_features_target(df, cfg["data"]["target"], cfg["data"]["drop_columns"])
    assert "duration" not in x.columns
    assert y[0] == 0


def test_brier_perfect():
    y = np.array([0, 1, 1, 0])
    p = np.array([0.0, 1.0, 1.0, 0.0])
    assert brier_score(y, p) == 0.0


def test_classification_scores_keys():
    y = np.array([0, 1, 0, 1])
    p = np.array([0.2, 0.8, 0.3, 0.7])
    scores = classification_scores(y, p)
    assert set(scores) == {"macro_f1", "brier", "pr_auc"}