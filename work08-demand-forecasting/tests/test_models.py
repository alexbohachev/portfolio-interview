"""Тести моделей: перевірка переваги LightGBM над Seasonal Naive та консистентності квантилів."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKTEST_PATH = ROOT / "manifests" / "backtest_results.json"


def test_lightgbm_beats_seasonal_naive_on_wape():
    assert BACKTEST_PATH.is_file(), "backtest_results.json відсутній"
    bt = json.loads(BACKTEST_PATH.read_text(encoding="utf-8"))
    summary = bt["summary"]
    
    lgb_wape = summary["lightgbm_wape"]
    naive_wape = summary["seasonal_naive_wape"]
    lift = summary["wape_reduction_pct"]
    
    assert lgb_wape < naive_wape, f"LightGBM ({lgb_wape}) не перевершив Seasonal Naive ({naive_wape})"
    assert lift >= 20.0, f"Приріст WAPE ({lift}%) менший за очікувані 20%"


def test_safety_stock_reduces_inventory_costs():
    bt = json.loads(BACKTEST_PATH.read_text(encoding="utf-8"))
    summary = bt["summary"]
    
    cost_lift = summary["cost_reduction_pct"]
    assert cost_lift >= 30.0, f"Скорочення витрат на запаси ({cost_lift}%) менше за 30%"


def test_conformal_calibration_guarantees_target_coverage():
    assert BACKTEST_PATH.is_file(), "backtest_results.json відсутній"
    bt = json.loads(BACKTEST_PATH.read_text(encoding="utf-8"))
    summary = bt["summary"]

    mean_cal_cov = summary["mean_calibrated_coverage_80"]
    mean_raw_cov = summary["mean_raw_coverage_80"]

    # Каліброване покриття повинно перевершувати сире та досягати номінальних 80%
    assert mean_cal_cov >= 0.80, f"Каліброване покриття ({mean_cal_cov * 100:.2f}%) нижче номінальних 80%"
    assert mean_cal_cov > mean_raw_cov, "Конформне калібрування мало підвищити емпіричне покриття"

    # Перевірка кожного окремого сезонного фолду (Spring, Summer, Autumn, Winter)
    for f in bt["folds"]:
        cal_cov = f["calibrated_quantile_coverage_80"]
        season = f["season"]
        assert cal_cov >= 0.80, f"Сезон '{season}' має каліброване покриття {cal_cov * 100:.2f}%, менше за 80%"
