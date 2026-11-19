"""План імпорту відкритого корпусу — dry-run, без завантаження контенту."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "sources.yaml"
OUT = ROOT / "artifacts" / "open_corpus_plan.json"


def main() -> int:
    data = yaml.safe_load(SRC.read_text(encoding="utf-8"))
    plan = {
        "target_docs": data.get("target_docs"),
        "current_mvp": data.get("current_mvp"),
        "steps": [],
    }
    for s in data.get("sources") or []:
        st = s.get("status", "?")
        item = {
            "id": s.get("id"),
            "status": st,
            "license": s.get("license"),
            "action": "keep" if st == "active" else "review_license_then_fetch",
        }
        if s.get("url"):
            item["url"] = s["url"]
        if s.get("path"):
            item["path"] = s["path"]
        plan["steps"].append(item)
    plan["steps"].append(
        {
            "id": "regenerate_golden",
            "status": "manual",
            "action": "30–60 hand-labeled Q/A після нового корпусу",
        }
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    print(f"\nWrote {OUT}")
    print("Наступний крок: підтвердити license → fetch → work02 seed → make all")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())