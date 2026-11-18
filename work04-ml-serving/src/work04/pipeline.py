from __future__ import annotations

import json
import time

from work04.config import load_config
from work04.paths import MANIFEST, REPORT
from work04.train import train_all


def run_all() -> dict:
    t0 = time.perf_counter()
    cfg = load_config()
    metrics = train_all(cfg)
    lines = [
        "# Звіт — робота 4 (ML serving)",
        "",
        "## Data contract",
        "- `data/DATA_CONTRACT.json`, synthetic `events.parquet`",
        "",
        "## Test metrics",
        f"- Baseline PR-AUC: **{metrics['baseline_test']['pr_auc']:.4f}**, Brier **{metrics['baseline_test']['brier']:.4f}**",
        f"- Candidate PR-AUC: **{metrics['candidate_test']['pr_auc']:.4f}**, Brier **{metrics['candidate_test']['brier']:.4f}**",
        f"- Поріг candidate (val cost): **{metrics['threshold_candidate']:.3f}**",
        "",
        "## Serving",
        "- `uvicorn work04.app_main:app` або pytest TestClient",
        "",
        f"_Час: {time.perf_counter() - t0:.1f} с._",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if MANIFEST.is_file():
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        manifest["last_run"] = metrics
        MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return metrics