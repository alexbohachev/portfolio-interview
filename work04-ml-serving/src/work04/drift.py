from __future__ import annotations

import numpy as np

from work04.config import load_config
from work04.data import FEATURES, load_events


def drift_summary(bundle: dict) -> dict:
    cfg = load_config()
    df = load_events().tail(500)
    ref = load_events().iloc[:2000]
    alerts = []
    for col in FEATURES:
        mu_r, mu_c = ref[col].mean(), df[col].mean()
        std_r = ref[col].std() or 1e-6
        z = abs(mu_c - mu_r) / std_r
        if z >= cfg["drift"]["alert_z_score"]:
            alerts.append({"feature": col, "z_score": float(z), "action": "alert"})
    return {
        "model_version": bundle["model_version"],
        "window_rows": len(df),
        "alerts": alerts,
        "drifted": bool(alerts),
    }