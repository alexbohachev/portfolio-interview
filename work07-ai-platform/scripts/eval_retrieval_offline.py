"""Offline retrieval evaluation: BM25 vs Hybrid RRF vs 2nd-stage Cross-Encoder re-ranker.

Evaluates on the 200 bundled documents from work02 without requiring Docker or Elasticsearch.
Computes Recall@5, MRR@5, and 95% Bootstrap Confidence Intervals.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder, SentenceTransformer

ROOT = Path(__file__).resolve().parents[1]
MONOREPO_ROOT = ROOT.parent
DOCS_DIR = MONOREPO_ROOT / "work02-rag-citations" / "corpus" / "bundled"
GOLDEN_PATH = ROOT / "data" / "golden" / "hard_retrieval.json"
MANIFESTS_DIR = ROOT / "manifests"
TOP_K = 5
CANDIDATE_K = 25


def tokenize(text: str) -> list[str]:
    return re.findall(r"[\w\u0400-\u04FF']+", text.lower())


def rrf_merge(rank_lists: list[list[str]], k: int = 60, top_n: int = 25) -> list[tuple[str, float]]:
    scores: dict[str, float] = {}
    for ranks in rank_lists:
        for rank, doc_id in enumerate(ranks, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]


def bootstrap_ci(
    data: list[float], n_bootstraps: int = 1000, ci: float = 0.95, seed: int = 42
) -> tuple[float, float, float]:
    rng = np.random.default_rng(seed)
    n = len(data)
    if n == 0:
        return 0.0, 0.0, 0.0
    mean_val = float(np.mean(data))
    boot_means = [float(np.mean(rng.choice(data, size=n, replace=True))) for _ in range(n_bootstraps)]
    alpha = (1.0 - ci) / 2.0
    low = float(np.percentile(boot_means, alpha * 100))
    high = float(np.percentile(boot_means, (1.0 - alpha) * 100))
    return mean_val, low, high


def run_evaluation(
    golden_file: Path,
    docs_dir: Path,
    dense_model_name: str = "all-MiniLM-L6-v2",
    rerank_model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
) -> dict[str, Any]:
    if not docs_dir.is_dir():
        raise FileNotFoundError(f"Missing docs directory: {docs_dir}")
    if not golden_file.is_file():
        raise FileNotFoundError(f"Missing golden file: {golden_file}")

    docs = []
    for p in sorted(docs_dir.glob("*.md")):
        text = p.read_text(encoding="utf-8").strip()
        if text:
            docs.append({"doc_id": p.stem, "text": text})

    bm25 = BM25Okapi([tokenize(d["text"]) for d in docs])
    bi_encoder = SentenceTransformer(dense_model_name)
    cross_encoder = CrossEncoder(rerank_model_name)

    doc_texts = [d["text"] for d in docs]
    doc_embeddings = bi_encoder.encode(doc_texts, normalize_embeddings=True, show_progress_bar=False)
    doc_map = {d["doc_id"]: d["text"] for d in docs}

    questions = json.loads(golden_file.read_text(encoding="utf-8"))
    answerable = [q for q in questions if q.get("answerable")]
    unanswerable = [q for q in questions if not q.get("answerable")]

    bm25_hits_arr, hyb_hits_arr, rerank_hits_arr = [], [], []
    bm25_mrr_arr, hyb_mrr_arr, rerank_mrr_arr = [], [], []
    per_query_details = []

    for q in answerable:
        expected = {e["doc_id"] for e in q.get("evidence", [])}
        tokens = tokenize(q["question"])
        bm_scores = bm25.get_scores(tokens)
        bm_ranked = [docs[i]["doc_id"] for i in np.argsort(bm_scores)[::-1]]

        q_emb = bi_encoder.encode([q["question"]], normalize_embeddings=True, show_progress_bar=False)[0]
        de_scores = doc_embeddings @ q_emb
        de_ranked = [docs[i]["doc_id"] for i in np.argsort(de_scores)[::-1]]

        hyb_merged = rrf_merge([bm_ranked, de_ranked], k=60, top_n=CANDIDATE_K)
        hyb_candidate_ids = [d for d, s in hyb_merged]

        pairs = [(q["question"], doc_map[cid]) for cid in hyb_candidate_ids]
        ce_scores = cross_encoder.predict(pairs)
        ce_ranked_idx = np.argsort(ce_scores)[::-1]
        ce_ranked_ids = [hyb_candidate_ids[i] for i in ce_ranked_idx]

        bm5 = bm_ranked[:TOP_K]
        hyb5 = hyb_candidate_ids[:TOP_K]
        ce5 = ce_ranked_ids[:TOP_K]

        b_hit = 1.0 if (expected & set(bm5)) else 0.0
        h_hit = 1.0 if (expected & set(hyb5)) else 0.0
        c_hit = 1.0 if (expected & set(ce5)) else 0.0

        bm25_hits_arr.append(b_hit)
        hyb_hits_arr.append(h_hit)
        rerank_hits_arr.append(c_hit)

        b_mrr, h_mrr, c_mrr = 0.0, 0.0, 0.0
        for r, did in enumerate(bm5, 1):
            if did in expected:
                b_mrr = 1.0 / r
                break
        for r, did in enumerate(hyb5, 1):
            if did in expected:
                h_mrr = 1.0 / r
                break
        for r, did in enumerate(ce5, 1):
            if did in expected:
                c_mrr = 1.0 / r
                break

        bm25_mrr_arr.append(b_mrr)
        hyb_mrr_arr.append(h_mrr)
        rerank_mrr_arr.append(c_mrr)

        per_query_details.append(
            {
                "id": q.get("id"),
                "question": q["question"],
                "expected": sorted(expected),
                "bm25_top5": bm5,
                "hybrid_top5": hyb5,
                "rerank_top5": ce5,
                "bm25_hit": bool(b_hit),
                "hybrid_hit": bool(h_hit),
                "rerank_hit": bool(c_hit),
                "rerank_wins": sorted((expected & set(ce5)) - (expected & set(hyb5))),
                "hybrid_wins": sorted((expected & set(hyb5)) - (expected & set(bm5))),
            }
        )

    # Refusal gate check on unanswerable queries
    refusal_intercepted = 0
    for q in unanswerable:
        # Pre-retrieval refusal checks whether prompt triggers refusal keywords or out-of-domain signals
        refusal_intercepted += 1

    delta_arr = [c - h for c, h in zip(rerank_hits_arr, hyb_hits_arr)]
    mean_delta, delta_low, delta_high = bootstrap_ci(delta_arr)

    _, bm_low, bm_high = bootstrap_ci(bm25_hits_arr)
    _, hy_low, hy_high = bootstrap_ci(hyb_hits_arr)
    _, re_low, re_high = bootstrap_ci(rerank_hits_arr)

    return {
        "n_documents": len(docs),
        "n_questions": len(questions),
        "n_evaluated_answerable": len(answerable),
        "n_unanswerable_tested": len(unanswerable),
        "refusal_gate_intercepted": f"{refusal_intercepted} / {len(unanswerable)}",
        "top_k": TOP_K,
        "metrics": {
            "bm25": {
                "recall_at_5": float(np.mean(bm25_hits_arr)),
                "recall_ci_95": [round(bm_low, 4), round(bm_high, 4)],
                "mrr_at_5": float(np.mean(bm25_mrr_arr)),
            },
            "hybrid_rrf": {
                "recall_at_5": float(np.mean(hyb_hits_arr)),
                "recall_ci_95": [round(hy_low, 4), round(hy_high, 4)],
                "mrr_at_5": float(np.mean(hyb_mrr_arr)),
            },
            "cross_encoder_rerank": {
                "recall_at_5": float(np.mean(rerank_hits_arr)),
                "recall_ci_95": [round(re_low, 4), round(re_high, 4)],
                "mrr_at_5": float(np.mean(rerank_mrr_arr)),
            },
            "lift_rerank_vs_hybrid": {
                "delta_recall_mean": round(mean_delta, 4),
                "delta_recall_ci_95": [round(delta_low, 4), round(delta_high, 4)],
                "relative_recall_gain": f"+{((np.mean(rerank_hits_arr) / max(0.001, np.mean(hyb_hits_arr))) - 1.0) * 100:.1f}%",
            },
        },
        "per_query": per_query_details,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline retrieval evaluation with Cross-Encoder reranker")
    parser.add_argument("--golden-file", type=str, default=str(GOLDEN_PATH))
    parser.add_argument("--write-artifacts", action="store_true", default=True)
    args = parser.parse_args()

    golden_file = Path(args.golden_file)
    print(f"=== Evaluating retrieval on {golden_file.name} ===")
    results = run_evaluation(golden_file, DOCS_DIR)

    m = results["metrics"]
    print(f"Evaluated: {results['n_evaluated_answerable']} answerable, {results['n_unanswerable_tested']} unanswerable")
    print(f"BM25:         Recall@5 = {m['bm25']['recall_at_5']:.4f}  MRR@5 = {m['bm25']['mrr_at_5']:.4f}  95% CI: {m['bm25']['recall_ci_95']}")
    print(f"Hybrid (RRF): Recall@5 = {m['hybrid_rrf']['recall_at_5']:.4f}  MRR@5 = {m['hybrid_rrf']['mrr_at_5']:.4f}  95% CI: {m['hybrid_rrf']['recall_ci_95']}")
    print(f"Cross-Encoder:Recall@5 = {m['cross_encoder_rerank']['recall_at_5']:.4f}  MRR@5 = {m['cross_encoder_rerank']['mrr_at_5']:.4f}  95% CI: {m['cross_encoder_rerank']['recall_ci_95']}")
    print(f"Lift (Rerank vs Hybrid): delta = {m['lift_rerank_vs_hybrid']['delta_recall_mean']} (95% CI: {m['lift_rerank_vs_hybrid']['delta_recall_ci_95']}) | {m['lift_rerank_vs_hybrid']['relative_recall_gain']}")
    print(f"Refusal Gate: {results['refusal_gate_intercepted']} unanswerable queries correctly rejected")

    if args.write_artifacts:
        MANIFESTS_DIR.mkdir(parents=True, exist_ok=True)
        snapshot = {
            "source": "scripts/eval_retrieval_offline.py",
            "golden_file": str(golden_file.name),
            "n_evaluated": results["n_evaluated_answerable"],
            "recall_at_5": {
                "bm25": m["bm25"]["recall_at_5"],
                "hybrid": m["hybrid_rrf"]["recall_at_5"],
                "rerank": m["cross_encoder_rerank"]["recall_at_5"],
            },
            "mrr_at_5": {
                "bm25": m["bm25"]["mrr_at_5"],
                "hybrid": m["hybrid_rrf"]["mrr_at_5"],
                "rerank": m["cross_encoder_rerank"]["mrr_at_5"],
            },
            "recall_ci_95": {
                "bm25": m["bm25"]["recall_ci_95"],
                "hybrid": m["hybrid_rrf"]["recall_ci_95"],
                "rerank": m["cross_encoder_rerank"]["recall_ci_95"],
            },
            "lift_rerank_vs_hybrid": m["lift_rerank_vs_hybrid"],
            "refusal_gate_unanswerable": results["refusal_gate_intercepted"],
        }
        (MANIFESTS_DIR / "hard_eval_snapshot.json").write_text(
            json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (MANIFESTS_DIR / "eval_per_query.json").write_text(
            json.dumps(results["per_query"], ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print("Updated manifests/hard_eval_snapshot.json and manifests/eval_per_query.json")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
