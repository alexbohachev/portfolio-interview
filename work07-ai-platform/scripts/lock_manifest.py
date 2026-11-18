"""Фіксує config_hash і SHA golden у manifests/test_manifest.json."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifests" / "test_manifest.json"
GOLDEN = ROOT / "data" / "golden" / "test.json"
COMPOSE = ROOT / "docker-compose.yml"


def sha16(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def main() -> None:
    manifest = {
        "work": "work07-ai-platform",
        "description": "Фінальний test golden + compose fingerprint для work07-v1.0",
        "golden_test_path": "data/golden/test.json",
        "golden_test_sha256_16": sha16(GOLDEN),
        "compose_sha256_16": sha16(COMPOSE),
        "eval_artifact": "artifacts/eval_results.json",
        "recommendation_artifact": "artifacts/recommendation_eval.json",
        "latency_artifact": "artifacts/latency_before_after.json",
    }
    if MANIFEST.is_file():
        prev = json.loads(MANIFEST.read_text(encoding="utf-8"))
        manifest["config_hash"] = prev.get("config_hash", sha16(COMPOSE))
    else:
        manifest["config_hash"] = sha16(COMPOSE)
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()