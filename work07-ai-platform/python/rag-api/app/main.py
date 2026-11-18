from __future__ import annotations

import os
from contextlib import asynccontextmanager

from elasticsearch import Elasticsearch
from fastapi import FastAPI
from pydantic import BaseModel, Field

INDEX = os.getenv("ES_INDEX", "agri-knowledge")
ES_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")


class SearchRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, alias="topK")

    model_config = {"populate_by_name": True}


class Hit(BaseModel):
    doc_id: str
    snippet: str
    score: float


def ensure_index(es: Elasticsearch) -> None:
    if es.indices.exists(index=INDEX):
        return
    es.indices.create(
        index=INDEX,
        mappings={
            "properties": {
                "doc_id": {"type": "keyword"},
                "title": {"type": "text"},
                "body": {"type": "text"},
            }
        },
    )
    es.index(
        index=INDEX,
        document={
            "doc_id": "agri_seed_001",
            "title": "Норми висіву пшениці",
            "body": "Рекомендована норма висіву озимої пшениці 4–5 млн насінин на гектар у північних районах.",
        },
        id="agri_seed_001",
    )
    es.indices.refresh(index=INDEX)


@asynccontextmanager
async def lifespan(app: FastAPI):
    es = Elasticsearch(ES_URL)
    ensure_index(es)
    app.state.es = es
    yield
    es.close()


app = FastAPI(title="rag-api", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/v1/knowledge/search")
def search(req: SearchRequest):
    es: Elasticsearch = app.state.es
    res = es.search(
        index=INDEX,
        query={"multi_match": {"query": req.query, "fields": ["title", "body"]}},
        size=req.top_k,
    )
    hits = [
        Hit(
            doc_id=(h["_source"].get("doc_id") or h["_id"]),
            snippet=(h["_source"].get("body") or "")[:300],
            score=float(h["_score"] or 0),
        )
        for h in res["hits"]["hits"]
    ]
    return {"hits": [h.model_dump() for h in hits]}