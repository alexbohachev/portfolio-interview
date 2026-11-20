from __future__ import annotations

from dataclasses import dataclass
import re

import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer


@dataclass
class RankedHit:
    chunk_id: str
    doc_id: str
    score: float
    text: str
    char_start: int
    char_end: int


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[\w\u0400-\u04FF']+", text.lower())


def rrf_merge(
    rank_lists: list[list[str]],
    k: int,
    top_k: int,
) -> list[tuple[str, float]]:
    scores: dict[str, float] = {}
    for ranks in rank_lists:
        for rank, cid in enumerate(ranks, start=1):
            scores[cid] = scores.get(cid, 0.0) + 1.0 / (k + rank)
    ordered = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ordered[:top_k]


class HybridRetriever:
    def __init__(
        self,
        chunk_ids: list[str],
        doc_ids: list[str],
        texts: list[str],
        char_starts: list[int],
        char_ends: list[int],
        model_name: str,
        rrf_k: int,
    ):
        self.chunk_ids = chunk_ids
        self.doc_ids = doc_ids
        self.texts = texts
        self.char_starts = char_starts
        self.char_ends = char_ends
        self.rrf_k = rrf_k
        self._bm25 = BM25Okapi([_tokenize(t) for t in texts])
        self._encoder = SentenceTransformer(model_name)
        self._dense = self._encoder.encode(texts, normalize_embeddings=True, show_progress_bar=False)

    def search_bm25(self, query: str, top_k: int) -> list[RankedHit]:
        scores = self._bm25.get_scores(_tokenize(query))
        idx = np.argsort(scores)[::-1][:top_k]
        return [
            RankedHit(
                self.chunk_ids[i],
                self.doc_ids[i],
                float(scores[i]),
                self.texts[i],
                self.char_starts[i],
                self.char_ends[i],
            )
            for i in idx
        ]

    def search_dense(self, query: str, top_k: int) -> list[RankedHit]:
        q = self._encoder.encode([query], normalize_embeddings=True, show_progress_bar=False)[0]
        sims = self._dense @ q
        idx = np.argsort(sims)[::-1][:top_k]
        return [
            RankedHit(
                self.chunk_ids[i],
                self.doc_ids[i],
                float(sims[i]),
                self.texts[i],
                self.char_starts[i],
                self.char_ends[i],
            )
            for i in idx
        ]

    def search_hybrid(self, query: str, top_k: int) -> list[RankedHit]:
        bm = [h.chunk_id for h in self.search_bm25(query, top_k * 3)]
        de = [h.chunk_id for h in self.search_dense(query, top_k * 3)]
        merged = rrf_merge([bm, de], self.rrf_k, top_k)
        id_to_idx = {cid: i for i, cid in enumerate(self.chunk_ids)}
        hits: list[RankedHit] = []
        for cid, score in merged:
            i = id_to_idx[cid]
            hits.append(
                RankedHit(
                    cid,
                    self.doc_ids[i],
                    score,
                    self.texts[i],
                    self.char_starts[i],
                    self.char_ends[i],
                )
            )
        return hits

    def search_rerank(
        self,
        query: str,
        top_k: int,
        reranker: object | None = None,
        candidate_k: int = 25,
    ) -> list[RankedHit]:
        candidates = self.search_hybrid(query, max(top_k * 4, candidate_k))
        if not candidates:
            return []
        if reranker is None:
            if not hasattr(self, "_cross_encoder"):
                from sentence_transformers import CrossEncoder

                self._cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
            reranker = getattr(self, "_cross_encoder")

        pairs = [(query, c.text) for c in candidates]
        scores = reranker.predict(pairs)  # type: ignore[attr-defined]
        ranked_indices = sorted(range(len(candidates)), key=lambda i: float(scores[i]), reverse=True)
        return [
            RankedHit(
                chunk_id=candidates[i].chunk_id,
                doc_id=candidates[i].doc_id,
                score=float(scores[i]),
                text=candidates[i].text,
                char_start=candidates[i].char_start,
                char_end=candidates[i].char_end,
            )
            for i in ranked_indices[:top_k]
        ]