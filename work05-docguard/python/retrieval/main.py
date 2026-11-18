"""Filtered BM25-lite search у межах allowed_doc_ids."""
from __future__ import annotations

import os
import re
from pathlib import Path

from fastapi import FastAPI, Request
from pydantic import BaseModel, Field

CORPUS = Path(os.getenv("CORPUS_DIR", "../work02-rag-citations/corpus/bundled")).resolve()
app = FastAPI(title="docguard-retrieval")
_DOCS: dict[str, str] = {}


def _tokenize(t: str) -> set[str]:
    return set(re.findall(r"[\w\u0400-\u04FF]+", t.lower()))


@app.on_event("startup")
def load_corpus() -> None:
    global _DOCS
    if not CORPUS.is_dir():
        return
    for p in CORPUS.glob("*.md"):
        _DOCS[p.stem] = p.read_text(encoding="utf-8")[:4000]


class SearchRequest(BaseModel):
    query: str
    allowed_doc_ids: list[str] = Field(alias="allowedDocIds")
    top_k: int = Field(default=5, alias="topK")

    model_config = {"populate_by_name": True}


@app.get("/health")
def health():
    return {"status": "ok", "docs": len(_DOCS)}


@app.post("/v1/search")
async def search(request: Request):
    raw = await request.body()
    if not raw:
        return {"hits": [], "error": "empty body"}
    import json

    data = json.loads(raw.decode("utf-8"))
    req = SearchRequest.model_validate(data)
    q = _tokenize(req.query)
    scored: list[tuple[float, str, str]] = []
    allowed = set(req.allowed_doc_ids)
    for doc_id, text in _DOCS.items():
        if doc_id not in allowed:
            continue
        dt = _tokenize(text)
        if not q:
            continue
        score = len(q & dt) / len(q)
        if score > 0:
            scored.append((score, doc_id, text[:300]))
    scored.sort(key=lambda x: -x[0])
    hits = [
        {"doc_id": doc_id, "snippet": snippet, "score": score}
        for score, doc_id, snippet in scored[: req.top_k]
    ]
    return {"hits": hits}