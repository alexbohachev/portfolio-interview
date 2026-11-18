from __future__ import annotations

from contextlib import asynccontextmanager

from elasticsearch import Elasticsearch
from fastapi import FastAPI
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer

from app.config import EMBED_MODEL, ES_URL, REFUSAL
from app.indexing import ensure_index
from app.qa import answer_query
from app.retrieve import search_bm25, search_hybrid


class SearchRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, alias="topK")
    mode: str = "hybrid"

    model_config = {"populate_by_name": True}


class QaRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, alias="topK")

    model_config = {"populate_by_name": True}


@asynccontextmanager
async def lifespan(app: FastAPI):
    es = Elasticsearch(ES_URL)
    model = SentenceTransformer(EMBED_MODEL)

    def embed(text: str) -> list[float]:
        return model.encode(text, normalize_embeddings=True).tolist()

    app.state.es = es
    app.state.embed = embed
    app.state.indexed_docs = ensure_index(es, embed)
    yield
    es.close()


app = FastAPI(title="rag-api", lifespan=lifespan)


@app.get("/health")
def health():
    es: Elasticsearch = app.state.es
    ready = es.ping()
    return {"status": "ok" if ready else "degraded", "indexed_docs": getattr(app.state, "indexed_docs", 0)}


@app.post("/v1/knowledge/search")
def search(req: SearchRequest):
    es: Elasticsearch = app.state.es
    embed = app.state.embed
    if req.mode == "bm25":
        hits = search_bm25(es, req.query, req.top_k)
    else:
        hits = search_hybrid(es, req.query, embed(req.query), req.top_k)
    return {
        "mode": req.mode,
        "hits": [h.__dict__ for h in hits],
    }


@app.post("/v1/knowledge/qa")
def qa(req: QaRequest):
    result = answer_query(app.state.es, app.state.embed, req.query, req.top_k)
    return {
        "answer": result.answer,
        "refused": result.refused,
        "mode": result.mode,
        "citations": [c.__dict__ for c in result.citations],
        "refusal_phrase": REFUSAL,
    }