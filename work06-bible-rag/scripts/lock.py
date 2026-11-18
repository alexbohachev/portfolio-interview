"""Manifest lock для work06."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from work06.config import load_config
from work06.paths import CONFIG

OUT = ROOT / "manifests" / "mvp_manifest.json"


def main() -> int:
    cfg = load_config(CONFIG)
    blob = json.dumps(cfg, sort_keys=True, ensure_ascii=False).encode("utf-8")
    h = hashlib.sha256(blob).hexdigest()[:16]
    manifest = {
        "work": "work06-bible-rag",
        "corpus_version": cfg.get("corpus_version"),
        "embed_model": cfg.get("embed_model"),
        "config_hash": h,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())