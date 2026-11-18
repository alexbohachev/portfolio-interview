"""Оцінка LLM-провайдера на до 30 dev-питань (ТЗ work02)."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from work02.config import load_config  # noqa: E402
from work02.corpus import corpus_fingerprint, load_bundled_corpus  # noqa: E402
from work02.gate import tune_refusal_threshold  # noqa: E402
from work02.paths import CONFIG, GOLDEN_DEV  # noqa: E402
from work02.qa_eval import citation_hits_evidence, evaluate_qa  # noqa: E402
from work02.retrieve import HybridRetriever  # noqa: E402

OUT = ROOT / "artifacts" / "llm_judge_results.json"
MAX_N = int(os.getenv("LLM_JUDGE_N", "30"))


def main() -> int:
    if not os.getenv("OPENAI_API_KEY"):
        print("SKIP: OPENAI_API_KEY not set", file=sys.stderr)
        return 0
    cfg = load_config(CONFIG)
    cfg = {**cfg, "llm": {**cfg["llm"], "enabled": True}}
    docs = load_bundled_corpus(ROOT / cfg["corpus"]["bundled_dir"])
    retriever = HybridRetriever(docs, cfg["retrieval"])
    dev = json.loads(GOLDEN_DEV.read_text(encoding="utf-8"))
    answerable = [q for q in dev if q.get("answerable") and q.get("evidence")][:MAX_N]
    threshold, _ = tune_refusal_threshold(retriever, dev, cfg["retrieval"]["top_k"])
    stats = evaluate_qa(retriever, {d.doc_id: d for d in docs}, answerable, threshold, cfg["retrieval"]["top_k"], cfg["llm"])
    result = {
        "provider": "openai",
        "model": cfg["llm"]["model"],
        "n_evaluated": len(answerable),
        "corpus_fingerprint": corpus_fingerprint(docs),
        "gate_threshold": threshold,
        "metrics": stats,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())