"""Повний запуск конвеєра прогнозування попиту: бектестинг, сегментний аналіз, збереження артефактів."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import pandas as pd

# Додаємо src до sys.path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from work08.backtest import run_rolling_backtest
from work08.config import ForecastingConfig
from work08.data import load_demand_data, validate_continuity
from work08.error_analysis import analyze_errors_by_segments
from work08.features import create_features
from work08.models import LightGBMPointForecaster, LightGBMQuantileForecaster


def main() -> int:
    cfg = ForecastingConfig()
    data_path = ROOT / cfg.data_path
    artifacts_dir = ROOT / cfg.artifacts_dir
    manifests_dir = ROOT / cfg.manifests_dir
    
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    manifests_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 65)
    print("=== WORK08: DEMAND FORECASTING & INVENTORY OPTIMIZATION ===")
    print("=" * 65)
    print(f"Data path: {data_path}")
    print(f"Horizon: {cfg.horizon_days} days | Backtest folds: {cfg.backtest_folds}")
    
    # 1. Завантаження даних
    df = load_demand_data(data_path)
    continuity = validate_continuity(df)
    broken_series = [k for k, ok in continuity.items() if not ok]
    if broken_series:
        print(f"ERROR: Виявлено розриви у часових рядах: {broken_series}", file=sys.stderr)
        return 1
    print(f"Завантажено {len(df)} записів по 20 часових рядах. Неперервність підтверджена 100%.")

    # 2. Суворий хронологічний бектестинг
    print("\n--- Запуск 4-фолдового хронологічного expanding-window бектестингу ---")
    bt_res = run_rolling_backtest(
        df=df,
        horizon_days=cfg.horizon_days,
        n_folds=cfg.backtest_folds,
        c_under=cfg.c_under,
        c_over=cfg.c_over,
    )
    
    summary = bt_res["summary"]
    print(f"Seasonal Naive WAPE:   {summary['seasonal_naive_wape'] * 100:.2f}%")
    print(f"LightGBM WAPE:         {summary['lightgbm_wape'] * 100:.2f}%")
    print(f"Зниження WAPE:         {summary['wape_reduction_pct']:.2f}% (перевага над бейзлайном)")
    print(f"Seasonal Naive Cost:   {summary['seasonal_naive_cost']:,.1f} у.о.")
    print(f"LightGBM Safety Cost:  {summary['lightgbm_safety_cost']:,.1f} у.о.")
    print(f"Скорочення витрат:     {summary['cost_reduction_pct']:.2f}% (за рахунок асиметричного ризику)")
    
    # 3. Сегментний аналіз помилок
    combined_preds = bt_res["combined_predictions"]
    err_segments = analyze_errors_by_segments(combined_preds)
    
    # 4. Фінальне навчання моделей на всій доступній історії для продакшн сервінгу
    print("\n--- Навчання фінальних моделей для продакшн-сервінгу ---")
    feat_df, feature_cols, target_col = create_features(df, horizon_days=cfg.horizon_days)
    
    final_point_model = LightGBMPointForecaster()
    final_point_model.fit(feat_df, feat_df[target_col].values, feature_cols)
    
    final_quantile_model = LightGBMQuantileForecaster(
        quantiles=cfg.quantiles,
        critical_ratio=cfg.critical_fractile,
    )
    final_quantile_model.fit(feat_df, feat_df[target_col].values, feature_cols)
    
    # Серіалізація
    joblib.dump(final_point_model, artifacts_dir / "model_point.joblib")
    joblib.dump(final_quantile_model, artifacts_dir / "model_quantile.joblib")
    print(f"Моделі серіалізовано до: {artifacts_dir}")

    # Збереження маніфестів
    clean_folds = []
    for f in bt_res["folds"]:
        f_clean = dict(f)
        clean_folds.append(f_clean)
        
    backtest_manifest = {
        "horizon_days": cfg.horizon_days,
        "n_folds": cfg.backtest_folds,
        "c_under": cfg.c_under,
        "c_over": cfg.c_over,
        "critical_fractile": round(cfg.critical_fractile, 4),
        "summary": summary,
        "folds": clean_folds,
    }
    
    (manifests_dir / "backtest_results.json").write_text(
        json.dumps(backtest_manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (manifests_dir / "segment_metrics.json").write_text(
        json.dumps(err_segments, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    
    print(f"Збережено артефакти: manifests/backtest_results.json та segment_metrics.json")
    print("=" * 65)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
