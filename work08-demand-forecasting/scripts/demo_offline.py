"""Короткий офлайн-вивід ключових результатів work08 без повторного навчання."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKTEST_PATH = ROOT / "manifests" / "backtest_results.json"
SEGMENTS_PATH = ROOT / "manifests" / "segment_metrics.json"


def main() -> int:
    if not BACKTEST_PATH.is_file():
        print("ERROR: спочатку запустіть py -3.13 scripts/run_pipeline.py", file=sys.stderr)
        return 1

    bt = json.loads(BACKTEST_PATH.read_text(encoding="utf-8"))
    summary = bt["summary"]
    
    print("=== WORK08: DEMAND FORECASTING (OFFLINE DEMO) ===")
    print(f"Horizon: {bt['horizon_days']} days | Backtest folds: {bt['n_folds']}")
    print(f"Seasonal Naive WAPE:   {summary['seasonal_naive_wape'] * 100:.2f}%")
    print(f"LightGBM WAPE:         {summary['lightgbm_wape'] * 100:.2f}% (зменшення на {summary['wape_reduction_pct']}%)")
    print(f"Seasonal Naive Cost:   {summary['seasonal_naive_cost']:,.1f} у.о.")
    print(f"LightGBM Safety Cost:  {summary['lightgbm_safety_cost']:,.1f} у.о. (скорочення на {summary['cost_reduction_pct']}%)")
    
    if SEGMENTS_PATH.is_file():
        seg = json.loads(SEGMENTS_PATH.read_text(encoding="utf-8"))
        print("\nСегментний зріз по SKU:")
        for s in seg.get("by_sku", []):
            print(f"  * {s['key']:16}: WAPE {s['lgb_wape']*100:.2f}% vs Naive {s['naive_wape']*100:.2f}% (+{s['wape_lift_pct']:.1f}% lift)")

    print("\nДеталі та аналіз помилок: REPORT.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
