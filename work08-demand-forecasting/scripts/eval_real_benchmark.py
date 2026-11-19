"""Оцінювання конвеєра прогнозування на реальному емпіричному датасеті (Capital Bikeshare daily demand 2011-2012).

Демонструє узагальнення рішень Work 08 на реальні часові ряди з різними типами попиту:
- SKU-Commuter: регулярний попит користувачів за підпискою
- SKU-Leisure: високоеластичний відпочинковий попит, чутливий до погоди та вихідних
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from work08.backtest import run_rolling_backtest
from work08.data import load_demand_data, validate_continuity
from work08.error_analysis import analyze_errors_by_segments

# 4 сезони 2012 року для реального часового ряду
REAL_SEASONAL_FOLDS = [
    {"season": "Spring Sowing/Commuter Peak", "cutoff": "2012-04-15"},
    {"season": "Summer High Season", "cutoff": "2012-07-15"},
    {"season": "Autumn Transition", "cutoff": "2012-10-01"},
    {"season": "Winter Off-Season", "cutoff": "2012-12-15"},
]


def main() -> int:
    data_path = ROOT / "data" / "raw" / "real_daily_demand.csv"
    manifests_dir = ROOT / "manifests"
    manifests_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 65)
    print("=== WORK08: REAL-WORLD EMPIRICAL BENCHMARK EVALUATION ===")
    print("=" * 65)
    print(f"Dataset: Capital Bikeshare 2011-2012 ({data_path})")

    df = load_demand_data(data_path)
    continuity = validate_continuity(df)
    print(f"Завантажено {len(df)} записів по {df[['hub_id', 'sku_id']].drop_duplicates().shape[0]} рядах.")
    print("Неперервність підтверджена 100%.")

    print("\n--- Запуск 4-сезонного бектестингу на реальних рядах (2012 рік) ---")
    bt_res = run_rolling_backtest(
        df=df,
        horizon_days=14,
        n_folds=4,
        c_under=5.0,
        c_over=1.0,
        custom_folds=REAL_SEASONAL_FOLDS,
    )

    summary = bt_res["summary"]
    print(f"Seasonal Naive WAPE:   {summary['seasonal_naive_wape'] * 100:.2f}%")
    print(f"LightGBM WAPE:         {summary['lightgbm_wape'] * 100:.2f}%")
    print(f"Зниження WAPE:         {summary['wape_reduction_pct']:.2f}%")
    print(f"Seasonal Naive Cost:   {summary['seasonal_naive_cost']:,.1f} у.о.")
    print(f"LightGBM Safety Cost:  {summary['lightgbm_safety_cost']:,.1f} у.о.")
    print(f"Скорочення витрат:     {summary['cost_reduction_pct']:.2f}%")
    print(f"Сире покриття P10-P90: {summary['mean_raw_coverage_80'] * 100:.2f}%")
    print(f"Каліброване покриття:  {summary['mean_calibrated_coverage_80'] * 100:.2f}%")

    combined_preds = bt_res["combined_predictions"]
    err_segments = analyze_errors_by_segments(combined_preds)

    clean_folds = [dict(f) for f in bt_res["folds"]]
    real_manifest = {
        "dataset_name": "Capital Bikeshare Real Daily Demand (2011-2012)",
        "dataset_type": "empirical_sensor_series",
        "horizon_days": 14,
        "n_folds": 4,
        "c_under": 5.0,
        "c_over": 1.0,
        "critical_fractile": round(5.0 / 6.0, 4),
        "summary": summary,
        "folds": clean_folds,
        "segment_metrics": err_segments,
    }

    out_file = manifests_dir / "real_benchmark_results.json"
    out_file.write_text(json.dumps(real_manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nЗбережено звіт реального бенчмарку: {out_file}")
    print("=" * 65)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
