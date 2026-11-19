"""Тести коректності та хронологічної ізоляції фолдів бектестингу."""
from __future__ import annotations

import pandas as pd
from pathlib import Path

from work08.data import load_demand_data
from work08.backtest import run_rolling_backtest

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "raw" / "historical_demand.csv"


def test_backtest_folds_are_chronological_and_contiguous():
    df = load_demand_data(DATA_PATH)
    horizon = 14
    n_folds = 4
    
    bt = run_rolling_backtest(df, horizon_days=horizon, n_folds=n_folds)
    folds = bt["folds"]
    
    assert len(folds) == n_folds
    
    for i, fold in enumerate(folds):
        train_end = pd.to_datetime(fold["train_end"])
        test_start = pd.to_datetime(fold["test_start"])
        test_end = pd.to_datetime(fold["test_end"])
        
        # 1. Тест суворо після завершення трейну
        assert test_start > train_end, f"Fold {i+1}: test_start ({test_start}) <= train_end ({train_end})"
        
        # 2. Тривалість тесту відповідає horizon_days
        days_span = (test_end - test_start).days + 1
        assert days_span == horizon, f"Fold {i+1}: span {days_span} != {horizon}"
        
        # 3. Суміжні фолди йдуть послідовно
        if i > 0:
            prev_end = pd.to_datetime(folds[i - 1]["test_end"])
            expected_next_start = prev_end + pd.Timedelta(days=1)
            assert test_start == expected_next_start, f"Розрив між фолдами {i} та {i+1}"
