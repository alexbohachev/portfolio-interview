"""Синтетичний датасет з event_time / available_at (data contract work04)."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw" / "events.parquet"
RNG = np.random.default_rng(42)


def main() -> None:
    n = 8000
    t0 = pd.Timestamp("2024-01-01", tz="UTC")
    event_time = t0 + pd.to_timedelta(RNG.integers(0, 120, n), unit="D")
    feature_ready = event_time - pd.to_timedelta(RNG.integers(0, 3, n), unit="h")
    hours_used = RNG.integers(1, 14, n)
    region = RNG.choice(["north", "south", "east"], n)
    equip = RNG.choice(["sprayer", "tractor", "harvester"], n)
    maint_score = RNG.normal(0, 1, n) + (hours_used > 10) * 0.8
    label_mature_at = event_time + pd.to_timedelta(RNG.integers(1, 14, n), unit="D")
    y = ((maint_score > 0.9) & (hours_used > 8)).astype(int)
    df = pd.DataFrame(
        {
            "event_id": [f"ev_{i:05d}" for i in range(n)],
            "event_time": event_time,
            "feature_available_at": feature_ready,
            "label_available_at": label_mature_at,
            "hours_used": hours_used,
            "region": region,
            "equipment_type": equip,
            "maint_score": maint_score,
            "target_breakdown_risk": y,
        }
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT, index=False)
    contract = {
        "target": "target_breakdown_risk",
        "horizon_days": "1-14 after event_time",
        "event_time": "event_time",
        "feature_available_at": "feature_available_at",
        "label_available_at": "label_available_at",
        "license": "synthetic CC0 portfolio",
    }
    (ROOT / "data" / "DATA_CONTRACT.json").write_text(
        json.dumps(contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"wrote {OUT} rows={len(df)} positive_rate={y.mean():.3f}")


if __name__ == "__main__":
    main()