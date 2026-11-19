"""Тести коректності та хронологічної ізоляції фолдів бектестингу."""
from __future__ import annotations

import pandas as pd
from pathlib import Path

from work08.data import load_demand_data
from work08.backtest import run_rolling_backtest

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "raw" / "historical_demand.csv"


def test_backtest_seasonal_folds_are_chronological_and_ex_ante():
    df = load_demand_data(DATA_PATH)
    horizon = 14
    n_folds = 4
    
    bt = run_rolling_backtest(df, horizon_days=horizon, n_folds=n_folds, use_seasonal_slices=True)
    folds = bt["folds"]
    
    assert len(folds) == n_folds
    
    prev_test_start = None
    for i, fold in enumerate(folds):
        train_end = pd.to_datetime(fold["train_end"])
        test_start = pd.to_datetime(fold["test_start"])
        test_end = pd.to_datetime(fold["test_end"])
        
        # 1. Тест суворо після завершення трейну (zero target leakage)
        assert test_start > train_end, f"Fold {i+1}: test_start ({test_start}) <= train_end ({train_end})"
        
        # 2. Тривалість тесту суворо відповідає операційному контракту H=14
        days_span = (test_end - test_start).days + 1
        assert days_span == horizon, f"Fold {i+1}: span {days_span} != {horizon}"
        
        # 3. Фолди хронологічно розширюються вперед у часі (expanding window)
        if prev_test_start is not None:
            assert test_start > prev_test_start, f"Fold {i+1}: test_start ({test_start}) <= prev ({prev_test_start})"
        prev_test_start = test_start

    # 4. Перевірка наявності ex-ante полів у прогнозах
    preds = bt["combined_predictions"]
    assert "ex_ante_temperature_c" in preds.columns
    assert "ex_ante_unit_price" in preds.columns
    assert "season" in preds.columns
    assert len(preds["season"].unique()) == n_folds


def test_backtest_fallback_contiguous_folds():
    df = load_demand_data(DATA_PATH)
    horizon = 14
    n_folds = 3
    
    bt = run_rolling_backtest(df, horizon_days=horizon, n_folds=n_folds, use_seasonal_slices=False)
    folds = bt["folds"]
    assert len(folds) == n_folds
    for fold in folds:
        assert (pd.to_datetime(fold["test_end"]) - pd.to_datetime(fold["test_start"])).days + 1 == horizon
