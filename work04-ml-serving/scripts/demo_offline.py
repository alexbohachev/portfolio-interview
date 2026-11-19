from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

BUNDLE = ROOT / "artifacts" / "model_bundle.joblib"
MANIFEST = ROOT / "manifests" / "test_manifest.json"


def main() -> int:
    if not BUNDLE.is_file():
        print("ERROR: .\\make.ps1 all (немає model_bundle.joblib)", file=sys.stderr)
        return 1
    from fastapi.testclient import TestClient
    from work04.app_main import app

    with TestClient(app) as client:
        h = client.get("/health").json()
        payload = {
            "hours_used": 10,
            "maint_score": 1.2,
            "region": "north",
            "equipment_type": "tractor",
            "use_candidate": True,
        }
        pred = client.post("/v1/predict", json=payload)
        r = pred.json()
    man = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.is_file() else {}
    print("=== work04 ML serving ===")
    print(f"config_hash: {man.get('config_hash')}")
    print("health:", json.dumps(h, ensure_ascii=False))
    if pred.status_code != 200:
        print("predict error:", r, file=sys.stderr)
        return 1
    print("predict:", json.dumps(r, ensure_ascii=False, indent=2)[:600])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())