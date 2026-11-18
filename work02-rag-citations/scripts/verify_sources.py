"""Перевірка data/sources.yaml перед відкритим корпусом."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "sources.yaml"


def main() -> int:
    if not SRC.is_file():
        print(f"missing {SRC}", file=sys.stderr)
        return 1
    data = yaml.safe_load(SRC.read_text(encoding="utf-8"))
    sources = data.get("sources") or []
    active = [s for s in sources if s.get("status") == "active"]
    planned = [s for s in sources if s.get("status") == "planned"]
    print(json.dumps({"active": len(active), "planned": len(planned), "target_docs": data.get("target_docs")}, indent=2))
    for s in planned:
        if not s.get("url") and not s.get("path"):
            print(f"WARN: planned source {s.get('id')} без url/path")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())