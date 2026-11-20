"""Retrieval + refusal-gate evaluation on the real Ukrainian Wikipedia agronomy corpus (corpus/wiki_uk).

Systems compared (single-label gold, whole articles as documents, top-5):
  bm25 | dense_en (all-MiniLM-L6-v2) | dense_ml (paraphrase-multilingual-MiniLM-L12-v2) |
  hybrid_en (BM25 + dense_en, RRF) | hybrid_ml (BM25 + dense_ml, RRF) | hybrid_ml + multilingual cross-encoder.

Also evaluates a real refusal gate: max dense cosine similarity, threshold tuned on a deterministic dev half of
all questions and measured on the held-out test half. Writes manifests/wiki_uk_eval.json.

Usage: python scripts/eval_wiki_uk.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder, SentenceTransformer

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpus" / "wiki_uk"
GOLDEN = ROOT / "data" / "golden" / "wiki_uk.json"
OUT = ROOT / "manifests" / "wiki_uk_eval.json"
TOP_K = 5
CAND_K = 25
EN_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
ML_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
CE_MODEL = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"


def tok(text: str) -> list[str]:
    return re.findall(r"[\wЀ-ӿ']+", text.lower())


def rrf(rank_lists: list[list[int]], k: int = 60, top_n: int = CAND_K) -> list[int]:
    scores: dict[int, float] = {}
    for ranks in rank_lists:
        for r, i in enumerate(ranks, 1):
            scores[i] = scores.get(i, 0.0) + 1.0 / (k + r)
    return [i for i, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]]


def boot(vals: list[float], n: int = 2000, seed: int = 42) -> list[float]:
    rng = np.random.default_rng(seed)
    arr = np.asarray(vals, dtype=float)
    means = [rng.choice(arr, size=len(arr), replace=True).mean() for _ in range(n)]
    return [round(float(np.percentile(means, 2.5)), 4), round(float(np.percentile(means, 97.5)), 4)]


def main() -> int:
    docs = sorted(CORPUS.glob("wiki_*.md"))
    texts = [p.read_text(encoding="utf-8") for p in docs]
    ids = [p.stem for p in docs]
    qs = json.loads(GOLDEN.read_text(encoding="utf-8"))
    ans = [q for q in qs if q["answerable"]]

    bm = BM25Okapi([tok(t) for t in texts])
    en, ml, ce = SentenceTransformer(EN_MODEL), SentenceTransformer(ML_MODEL), CrossEncoder(CE_MODEL)
    d_en = en.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    d_ml = ml.encode(texts, normalize_embeddings=True, show_progress_bar=False)

    ranks: dict[str, list[list[int]]] = {k: [] for k in ["bm25", "dense_en", "dense_ml", "hybrid_en", "hybrid_ml", "hybrid_ml_rerank"]}
    for q in ans:
        s_bm = np.argsort(bm.get_scores(tok(q["question"])))[::-1]
        s_en = np.argsort(d_en @ en.encode([q["question"]], normalize_embeddings=True, show_progress_bar=False)[0])[::-1]
        s_ml = np.argsort(d_ml @ ml.encode([q["question"]], normalize_embeddings=True, show_progress_bar=False)[0])[::-1]
        h_en = rrf([s_bm.tolist(), s_en.tolist()])
        h_ml = rrf([s_bm.tolist(), s_ml.tolist()])
        ce_scores = ce.predict([(q["question"], texts[i]) for i in h_ml])
        reranked = [h_ml[i] for i in np.argsort(ce_scores)[::-1]]
        for k, v in [("bm25", s_bm), ("dense_en", s_en), ("dense_ml", s_ml)]:
            ranks[k].append(v.tolist()[:TOP_K])
        ranks["hybrid_en"].append(h_en[:TOP_K])
        ranks["hybrid_ml"].append(h_ml[:TOP_K])
        ranks["hybrid_ml_rerank"].append(reranked[:TOP_K])

    gold = [ids.index(q["doc_id"]) for q in ans]
    per_sys: dict[str, dict] = {}
    hits: dict[str, list[float]] = {}
    for name, lists in ranks.items():
        hit = [1.0 if g in r else 0.0 for g, r in zip(gold, lists)]
        hit1 = [1.0 if r and r[0] == g else 0.0 for g, r in zip(gold, lists)]
        rr = [(1.0 / (r.index(g) + 1)) if g in r else 0.0 for g, r in zip(gold, lists)]
        hits[name] = hit
        per_sys[name] = {
            "recall_at_5": round(float(np.mean(hit)), 4), "recall_at_5_ci95": boot(hit),
            "recall_at_1": round(float(np.mean(hit1)), 4), "mrr_at_5": round(float(np.mean(rr)), 4),
        }

    def delta(a: str, b: str) -> dict:
        d = [x - y for x, y in zip(hits[a], hits[b])]
        return {"mean": round(float(np.mean(d)), 4), "ci95": boot(d)}

    lifts = {
        "hybrid_en_vs_bm25": delta("hybrid_en", "bm25"),
        "hybrid_ml_vs_hybrid_en": delta("hybrid_ml", "hybrid_en"),
        "rerank_vs_hybrid_ml": delta("hybrid_ml_rerank", "hybrid_ml"),
        "rerank_vs_hybrid_en": delta("hybrid_ml_rerank", "hybrid_en"),
    }

    # Refusal gate: max dense (multilingual) cosine, tuned on dev half, measured on test half.
    maxsim = [float((d_ml @ ml.encode([q["question"]], normalize_embeddings=True, show_progress_bar=False)[0]).max()) for q in qs]
    rng = np.random.default_rng(42)
    dev_idx, test_idx = set(), set()
    for flag in (True, False):  # stratified: split answerable and unanswerable separately
        grp = rng.permutation([i for i, q in enumerate(qs) if q["answerable"] == flag]).tolist()
        dev_idx |= set(grp[: len(grp) // 2])
        test_idx |= set(grp[len(grp) // 2:])
    cand = sorted(set(round(s, 3) for s in maxsim))

    def acc(idx: set[int], t: float) -> float:
        return float(np.mean([(maxsim[i] >= t) == qs[i]["answerable"] for i in idx]))

    best_t = max(cand, key=lambda t: (acc(dev_idx, t), -abs(t - np.median(maxsim))))
    test_ans = [i for i in test_idx if qs[i]["answerable"]]
    test_un = [i for i in test_idx if not qs[i]["answerable"]]
    gate = {
        "signal": "max cosine similarity (dense_ml)", "threshold_tuned_on_dev": best_t,
        "dev_accuracy": round(acc(dev_idx, best_t), 4), "test_accuracy": round(acc(test_idx, best_t), 4),
        "test_n_answerable": len(test_ans), "test_n_unanswerable": len(test_un),
        "test_correct_refusals": f"{sum(maxsim[i] < best_t for i in test_un)} / {len(test_un)}",
        "test_false_refusals": f"{sum(maxsim[i] < best_t for i in test_ans)} / {len(test_ans)}",
    }

    # Lexical overlap between each question and its target article (share of question tokens found in the article).
    overlap = [len(set(tok(q["question"])) & set(tok(texts[g]))) / max(1, len(set(tok(q["question"])))) for q, g in zip(ans, gold)]
    result = {
        "corpus": {"source": "uk.wikipedia.org (CC BY-SA 4.0)", "n_documents": len(docs)},
        "n_answerable_questions": len(ans), "n_unanswerable_questions": len(qs) - len(ans),
        "models": {"dense_en": EN_MODEL, "dense_ml": ML_MODEL, "cross_encoder": CE_MODEL},
        "mean_question_token_overlap_with_target_article": round(float(np.mean(overlap)), 3),
        "systems": per_sys, "paired_lifts_recall_at_5": lifts, "refusal_gate": gate,
        "caveats": ["single-label gold under-counts other relevant articles", "whole articles embedded; models truncate long inputs",
                     "small n: read confidence intervals, not point estimates", "gate test half is small"],
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    for k, v in per_sys.items():
        print(f"{k:18s} R@5 {v['recall_at_5']:.3f} {v['recall_at_5_ci95']}  R@1 {v['recall_at_1']:.3f}  MRR@5 {v['mrr_at_5']:.3f}")
    for k, v in lifts.items():
        print(f"lift {k}: {v}")
    print("gate:", gate)
    return 0


if __name__ == "__main__":
    sys.exit(main())
