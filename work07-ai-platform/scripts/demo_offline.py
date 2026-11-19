"""Метрики work07 без Docker (читає artifacts + manifest)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "artifacts" / "eval_results.json"
MANIFEST = ROOT / "manifests" / "test_manifest.json"
REPORT = ROOT / "REPORT.md"


def main() -> int:
    print("=== work07 AI platform (offline) ===")
    if MANIFEST.is_file():
        m = json.loads(MANIFEST.read_text(encoding="utf-8"))
        print(f"config_hash: {m.get('config_hash')}")
    if EVAL.is_file():
        ev = json.loads(EVAL.read_text(encoding="utf-8"))
        test = ev.get("test") or ev.get("hybrid_test") or {}
        rec = ev.get("recommendations_test") or ev.get("recommendations") or {}
        if "recall_at_5" in test or "recall_at_k" in test:
            rk = test.get("recall_at_5", test.get("recall_at_k"))
            print(f"retrieval test Recall@5 hybrid: {rk}")
        if rec:
            print(f"recommendations Hit@3: {rec.get('hit_at_3', rec.get('hit_at_k'))}")
    elif REPORT.is_file():
        print("(немає artifacts/eval_results.json — див. REPORT.md)")
    print("\nLive: docker compose up + .\\make.ps1 smoke")
    print("Демо: scripts\\demo.ps1 · DEMO.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())