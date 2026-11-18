"""Hit@3 і precision@3 рекомендацій (golden recommendations_*)."""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from shared.recommendation import load_catalog, pick_actions  # noqa: E402

RAG_URL = os.getenv("RAG_API_URL", "http://localhost:8090").rstrip("/")
OUT = ROOT / "artifacts" / "recommendation_eval.json"


def search_hybrid(question: str) -> list[dict]:
    payload = json.dumps({"query": question, "topK": 5, "mode": "hybrid"}).encode("utf-8")
    req = urllib.request.Request(
        f"{RAG_URL}/v1/knowledge/search",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        body = json.loads(r.read().decode())
    return body.get("hits") or []


def citation_supported(action: dict, hits: list[dict]) -> bool:
    doc_id = action.get("citation_doc_id") or ""
    if not doc_id:
        return False
    return any(h.get("doc_id") == doc_id for h in hits)


def eval_split(items: list[dict], catalog: list[dict]) -> dict:
    hit = 0
    precision_sum = 0.0
    citation_ok = 0
    for row in items:
        note = row["note"]
        acceptable = set(row["acceptable_action_ids"])
        question = f"Рекомендації для поля {row['field_id']}: {note}"
        hits = search_hybrid(question)
        actions = pick_actions(note, hits, catalog, top=3)
        pred_ids = [a["action_id"] for a in actions]
        if set(pred_ids) & acceptable:
            hit += 1
        if actions:
            precision_sum += len(set(pred_ids) & acceptable) / len(actions)
        citation_ok += sum(1 for a in actions if citation_supported(a, hits) and a["action_id"] in acceptable)
    n = len(items) or 1
    return {
        "n": len(items),
        "hit_at_3": hit / n,
        "precision_at_3": precision_sum / n,
        "citation_support_rate": citation_ok / (n * 3),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=("test", "dev"), default="test")
    args = parser.parse_args()
    golden = ROOT / "data" / "golden" / f"recommendations_{args.split}.json"
    if not golden.is_file():
        print(f"FAIL: {golden} — run build_recommendation_golden.py", file=sys.stderr)
        return 1
    items = json.loads(golden.read_text(encoding="utf-8"))
    catalog = load_catalog(str(ROOT / "config" / "actions_catalog.json"))
    stats = eval_split(items, catalog)
    result = {"split": args.split, "golden": str(golden.relative_to(ROOT)), **stats}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())