"""Швидке демо без повного переіндексування (читає artifacts/results.json)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from work02.paths import ARTIFACTS, GOLDEN_TEST, MANIFEST


def main() -> int:
    res_path = ARTIFACTS / "results.json"
    if not res_path.is_file():
        print("ERROR: спочатку .\\make.ps1 all", file=sys.stderr)
        return 1
    res = json.loads(res_path.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    print("=== work02 RAG demo (offline) ===")
    print(f"config_hash: {manifest.get('config_hash')}")
    print(f"n_docs: {res.get('n_docs')}  corpus_fp: {res.get('corpus_fingerprint')}")
    print(f"gate threshold: {res.get('retrieval_gate_threshold')}")
    b = res["baseline_retrieval_test"]
    c = res["candidate_retrieval_test"]
    print(f"Recall@5  BM25={b['recall_at_k']:.4f}  hybrid={c['recall_at_k']:.4f}")
    qa = res["qa_test"]
    print(
        "QA test:",
        f"refusals {qa.get('correct_refusals')}",
        f"citations {qa.get('citation_accuracy')}",
        f"gold overlap {qa.get('answer_contains_gold')}",
    )
    sample = json.loads(GOLDEN_TEST.read_text(encoding="utf-8"))[0]
    print(f"\nПриклад test-питання: {sample['question']}")
    print("Див. REPORT.md для повної таблиці.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())