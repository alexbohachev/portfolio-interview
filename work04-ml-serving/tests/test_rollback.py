"""Rollback: bundle містить узгоджені model + preprocessing + версії."""
from __future__ import annotations

import joblib
import pandas as pd

from work04.data import align_columns, load_events, matrix
from work04.paths import ARTIFACTS


def test_bundle_versions_consistent():
    path = ARTIFACTS / "model_bundle.joblib"
    if not path.is_file():
        import pytest

        pytest.skip("run work04 all")
    b = joblib.load(path)
    df = load_events().tail(100)
    x, _, cols = matrix(df)
    assert cols == b["feature_columns"]
    x = align_columns(x, b["feature_columns"])
    prob = b["candidate"].predict_proba(x)[:, 1]
    assert len(prob) == len(df)
    assert b["model_version"] == "work04-v1.0"
    assert b["preprocessing_version"] == "cols-v1"