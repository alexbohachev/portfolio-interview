from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MF = ROOT / "manifests" / "fault_manifest.json"


def main() -> int:
    if not MF.is_file():
        print("missing fault_manifest.json", file=sys.stderr)
        return 1
    m = json.loads(MF.read_text(encoding="utf-8"))
    print("=== work03 agent workflow ===")
    print(f"fault scenarios: {m.get('n_scenarios')}/{m.get('target_tz')}")
    print("groups:", json.dumps(m.get("groups"), ensure_ascii=False))
    print("\nДля живого тестування: docker compose up -d -> ./gradlew bootRun -> bash scripts/reliability_demo.sh (або demo.ps1)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())