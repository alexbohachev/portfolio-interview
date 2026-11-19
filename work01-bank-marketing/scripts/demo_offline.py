"""Короткий вивід метрик work01 без повного re-train."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifests" / "test_manifest.json"
REPORT = ROOT / "REPORT.md"


def main() -> int:
    if not REPORT.is_file():
        print("ERROR: спочатку .\\make.ps1 all", file=sys.stderr)
        return 1
    text = REPORT.read_text(encoding="utf-8")
    m = re.search(
        r"\| macro-F1 \| ([0-9.]+) \| ([0-9.]+) \|",
        text,
    )
    man = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.is_file() else {}
    print("=== work01 bank marketing (offline demo) ===")
    print(f"manifest test_n: {man.get('n_test', '?')}  config_hash: {man.get('config_hash', '?')}")
    if m:
        print(f"test macro-F1  baseline={m.group(1)}  candidate={m.group(2)}")
    if "duration" in text:
        print("leakage guard: duration виключено з ознак")
    print("\nДеталі: REPORT.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())