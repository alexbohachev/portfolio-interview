"""Метрики work07 без Docker (artifacts або committed snapshot)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "artifacts" / "eval_results.json"
SNAPSHOT = ROOT / "manifests" / "eval_snapshot.json"
MANIFEST = ROOT / "manifests" / "test_manifest.json"


def _print_eval(ev: dict) -> None:
    if "recall_at_5" in ev and isinstance(ev["recall_at_5"], dict):
        print(f"Recall@5 hybrid: {ev['recall_at_5'].get('hybrid')}")
        print(f"Recall@5 bm25: {ev['recall_at_5'].get('bm25')}")
    rec = ROOT / "artifacts" / "recommendation_eval.json"
    if rec.is_file():
        r = json.loads(rec.read_text(encoding="utf-8"))
        print(f"Hit@3 recs: {r.get('hit_at_3')}")
    elif "hit_at_3" in ev:
        print(f"Hit@3 recs: {ev.get('hit_at_3')}")


def _print_snapshot(snap: dict) -> None:
    print(f"snapshot: {snap.get('source')}")
    print(f"Recall@5 hybrid: {snap.get('recall_at_5', {}).get('hybrid')}")
    print(f"Hit@3 recs: {snap.get('hit_at_3')}")
    print(f"latency speedup p50: {snap.get('latency_speedup_p50')}x")
    print(f"smoke: {snap.get('smoke')}")


def main() -> int:
    print("=== work07 AI platform (offline) ===")
    if MANIFEST.is_file():
        m = json.loads(MANIFEST.read_text(encoding="utf-8"))
        print(f"config_hash: {m.get('config_hash')}")
    if EVAL.is_file():
        ev = json.loads(EVAL.read_text(encoding="utf-8"))
        print("(from artifacts/eval_results.json)")
        _print_eval(ev)
    elif SNAPSHOT.is_file():
        _print_snapshot(json.loads(SNAPSHOT.read_text(encoding="utf-8")))
    else:
        print("Немає eval_results.json — див. manifests/eval_snapshot.json або REPORT.md")
    print("\nLive: docker compose up + .\\make.ps1 smoke")
    print("Демо: scripts\\demo.ps1 · DEMO.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())