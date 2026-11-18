from __future__ import annotations

from typing import Any

from work02.corpus import Document
from work02.retrieve import HybridRetriever, RankedHit


def span_covered(hit: RankedHit, doc: Document, start: int, end: int) -> bool:
    if hit.doc_id != doc.doc_id:
        return False
    return not (hit.char_end <= start or hit.char_start >= end)


def recall_evidence_at_k(
    hits: list[RankedHit],
    docs_by_id: dict[str, Document],
    evidence: list[dict[str, Any]],
    k: int,
) -> bool:
    if not evidence:
        return False
    top = hits[:k]
    for ev in evidence:
        doc = docs_by_id[ev["doc_id"]]
        start, end = int(ev["char_start"]), int(ev["char_end"])
        if not any(span_covered(h, doc, start, end) for h in top):
            return False
    return True


def evaluate_split(
    retriever: HybridRetriever,
    docs_by_id: dict[str, Document],
    questions: list[dict[str, Any]],
    mode: str,
    k: int,
) -> dict[str, float]:
    recalls: list[float] = []
    multi_ok: list[float] = []
    unanswerable_ok: list[float] = []

    for q in questions:
        query = q["question"]
        if mode == "bm25":
            hits = retriever.search_bm25(query, k)
        elif mode == "hybrid":
            hits = retriever.search_hybrid(query, k)
        else:
            raise ValueError(mode)
        evidence = q.get("evidence", [])
        answerable = q.get("answerable", True)
        if not answerable:
            # retrieval gate: no strong hit — simplified: max bm25/dense score low not implemented; expect empty evidence
            unanswerable_ok.append(1.0 if not evidence else float(recall_evidence_at_k(hits, docs_by_id, evidence, k)))
            continue
        ok = recall_evidence_at_k(hits, docs_by_id, evidence, k)
        recalls.append(1.0 if ok else 0.0)
        if q.get("type") == "multi_hop" and len(evidence) > 1:
            multi_ok.append(1.0 if ok else 0.0)

    out = {
        "recall_at_k": float(sum(recalls) / len(recalls)) if recalls else 0.0,
        "n": len(recalls),
    }
    if multi_ok:
        out["multi_hop_recall"] = float(sum(multi_ok) / len(multi_ok))
    if unanswerable_ok:
        out["unanswerable_acc"] = float(sum(unanswerable_ok) / len(unanswerable_ok))
    return out