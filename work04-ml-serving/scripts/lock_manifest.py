from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifests" / "test_manifest.json"
CONFIG = ROOT / "config" / "default.yaml"
BUNDLE = ROOT / "artifacts" / "model_bundle.joblib"


def sha16(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def main() -> None:
    m = {
        "work": "work04-ml-serving",
        "description": "model_bundle.joblib — model + preprocessing + thresholds",
        "artifact": "artifacts/model_bundle.joblib",
        "config_hash": sha16(CONFIG),
        "bundle_sha256_16": sha16(BUNDLE) if BUNDLE.is_file() else None,
    }
    MANIFEST.write_text(json.dumps(m, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(m, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()