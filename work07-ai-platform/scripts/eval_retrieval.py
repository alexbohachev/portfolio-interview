"""Recall@5 і MRR@5 на golden work07 (test за замовчуванням). Потрібен rag-api."""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOLDEN_DIR = ROOT / "data" / "golden"
RAG_URL = os.getenv("RAG_API_URL", "http://localhost:8090").rstrip("/")
TOP_K = 5
ARTIFACTS = ROOT / "artifacts"
OUT = ARTIFACTS / "eval_results.json"


def post_search(query: str, mode: str) -> list[str]:
    payload = json.dumps({"query": query, "topK": TOP_K, "mode": mode}).encode("utf-8")
    req = urllib.request.Request(
        f"{RAG_URL}/v1/knowledge/search",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        body = json.loads(r.read().decode())
    return [h.get("doc_id", "") for h in body.get("hits", [])]


def expected_doc_ids(item: dict) -> set[str]:
    ids = {e["doc_id"] for e in item.get("evidence", []) if e.get("doc_id")}
    if not ids and item.get("answerable") is False:
        return set()
    return ids


def metrics_at_k(items: list[dict], mode: str) -> tuple[float, float, int]:
    if not items:
        return 0.0, 0.0, 0
    recall_hits = 0
    mrr_sum = 0.0
    evaluated = 0
    for item in items:
        expected = expected_doc_ids(item)
        if not expected:
            continue
        evaluated += 1
        ranked = post_search(item["question"], mode)[:TOP_K]
        retrieved = set(ranked)
        if expected & retrieved:
            recall_hits += 1
        for rank, doc_id in enumerate(ranked, start=1):
            if doc_id in expected:
                mrr_sum += 1.0 / rank
                break
    recall = recall_hits / evaluated if evaluated else 0.0
    mrr = mrr_sum / evaluated if evaluated else 0.0
    return recall, mrr, evaluated


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=("test", "dev"), default="test")
    args = parser.parse_args()

    golden = GOLDEN_DIR / f"{args.split}.json"
    if not golden.is_file():
        print(f"FAIL: missing golden {golden} — run scripts/build_golden_150.py", file=sys.stderr)
        return 1
    items = json.loads(golden.read_text(encoding="utf-8"))
    bm25_r, bm25_m, n = metrics_at_k(items, "bm25")
    hyb_r, hyb_m, _ = metrics_at_k(items, "hybrid")
    result = {
        "split": args.split,
        "golden_path": str(golden.relative_to(ROOT)),
        "n_questions": len(items),
        "n_evaluated": n,
        "top_k": TOP_K,
        "recall_at_5": {"bm25": bm25_r, "hybrid": hyb_r},
        "mrr_at_5": {"bm25": bm25_m, "hybrid": hyb_m},
        "delta_hybrid_minus_bm25_recall": hyb_r - bm25_r,
    }
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())