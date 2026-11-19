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


def test_conformal_calibration_achieves_target_coverage_on_synthetic_folds():
    assert BACKTEST_PATH.is_file(), "backtest_results.json відсутній"
    bt = json.loads(BACKTEST_PATH.read_text(encoding="utf-8"))
    summary = bt["summary"]

    mean_cal_cov = summary["mean_calibrated_coverage_80"]
    mean_raw_cov = summary["mean_raw_coverage_80"]

    # Каліброване покриття повинно перевершувати сире та досягати номінальних 80% на тестових вікнах
    assert mean_cal_cov >= 0.80, f"Каліброване покриття ({mean_cal_cov * 100:.2f}%) нижче номінальних 80%"
    assert mean_cal_cov > mean_raw_cov, "Конформне калібрування мало підвищити емпіричне покриття"

    # Перевірка кожного окремого сезонного фолду (Spring, Summer, Autumn, Winter)
    for f in bt["folds"]:
        cal_cov = f["calibrated_quantile_coverage_80"]
        season = f["season"]
        assert cal_cov >= 0.80, f"Сезон '{season}' має каліброване покриття {cal_cov * 100:.2f}%, менше за 80%"


def test_real_benchmark_baseline_victory_and_conformal_lift():
    real_path = ROOT / "manifests" / "real_benchmark_results.json"
    assert real_path.is_file(), "real_benchmark_results.json відсутній"
    res = json.loads(real_path.read_text(encoding="utf-8"))
    summary = res["summary"]

    # На реальних даних Bikeshare сезонний бейзлайн виграє у LightGBM за WAPE та вартістю
    assert summary["seasonal_naive_wape"] < summary["lightgbm_wape"], "Бейзлайн мав виграти за WAPE на Bikeshare"
    assert summary["seasonal_naive_cost"] < summary["lightgbm_safety_cost"], "Бейзлайн мав мати менші витрати на Bikeshare"

    # CQR калібрування суттєво піднімає покриття (з 26.79% до 75.89%)
    assert summary["mean_calibrated_coverage_80"] > summary["mean_raw_coverage_80"] + 0.30, "CQR мало підняти покриття більш ніж на 30 п.п."

