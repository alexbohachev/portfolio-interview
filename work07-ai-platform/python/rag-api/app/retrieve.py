from __future__ import annotations

from dataclasses import dataclass

from elasticsearch import Elasticsearch

from app.config import INDEX, RRF_K


@dataclass
class Hit:
    doc_id: str
    snippet: str
    score: float
    title: str = ""


def _rrf_merge(rank_lists: list[list[str]], k: int, top_k: int) -> list[tuple[str, float]]:
    scores: dict[str, float] = {}
    for ranks in rank_lists:
        for rank, doc_id in enumerate(ranks, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]


def _source_map(es: Elasticsearch, ids: list[str]) -> dict[str, dict]:
    if not ids:
        return {}
    res = es.mget(index=INDEX, ids=ids)
    out = {}
    for doc in res.get("docs", []):
        if doc.get("found"):
            out[doc["_id"]] = doc["_source"]
    return out


def _prefix_filter(doc_id_prefix: str | None) -> list[dict]:
    if not doc_id_prefix:
        return []
    return [{"prefix": {"doc_id": doc_id_prefix}}]


def search_bm25(es: Elasticsearch, query: str, top_k: int, doc_id_prefix: str | None = None) -> list[Hit]:
    bool_q: dict = {"must": [{"multi_match": {"query": query, "fields": ["title", "body"]}}]}
    filt = _prefix_filter(doc_id_prefix)
    if filt:
        bool_q["filter"] = filt
    res = es.search(
        index=INDEX,
        query={"bool": bool_q},
        size=top_k,
    )
    return [_to_hit(h) for h in res["hits"]["hits"]]


def search_dense(es: Elasticsearch, query_vector: list[float], top_k: int, doc_id_prefix: str | None = None) -> list[Hit]:
    knn: dict = {
        "field": "embedding",
        "query_vector": query_vector,
        "k": top_k,
        "num_candidates": max(50, top_k * 5),
    }
    filt = _prefix_filter(doc_id_prefix)
    if filt:
        knn["filter"] = filt
    res = es.search(
        index=INDEX,
        knn=knn,
        size=top_k,
    )
    return [_to_hit(h) for h in res["hits"]["hits"]]


def search_hybrid(
    es: Elasticsearch, query: str, query_vector: list[float], top_k: int, doc_id_prefix: str | None = None
) -> list[Hit]:
    bm = search_bm25(es, query, top_k * 2, doc_id_prefix)
    de = search_dense(es, query_vector, top_k * 2, doc_id_prefix)
    merged = _rrf_merge(
        [[h.doc_id for h in bm], [h.doc_id for h in de]],
        RRF_K,
        top_k,
    )
    sources = _source_map(es, [doc_id for doc_id, _ in merged])
    hits: list[Hit] = []
    for doc_id, score in merged:
        src = sources.get(doc_id, {})
        body = src.get("body", "")
        hits.append(
            Hit(
                doc_id=doc_id,
                title=src.get("title", ""),
                snippet=body[:300],
                score=score,
            )
        )
    return hits


def _to_hit(h: dict) -> Hit:
    src = h.get("_source", {})
    return Hit(
        doc_id=src.get("doc_id") or h.get("_id"),
        title=src.get("title", ""),
        snippet=(src.get("body") or "")[:300],
        score=float(h.get("_score") or 0.0),
    )