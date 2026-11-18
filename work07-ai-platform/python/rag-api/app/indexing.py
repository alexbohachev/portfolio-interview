from __future__ import annotations

from pathlib import Path

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from app.config import CORPUS_DIR, EMBED_DIM, INDEX


def index_mapping() -> dict:
    return {
        "properties": {
            "doc_id": {"type": "keyword"},
            "title": {"type": "text"},
            "body": {"type": "text"},
            "embedding": {
                "type": "dense_vector",
                "dims": EMBED_DIM,
                "index": True,
                "similarity": "cosine",
            },
        }
    }


def load_markdown_docs(corpus_dir: str) -> list[dict]:
    root = Path(corpus_dir)
    if not root.is_dir():
        return []
    docs = []
    for path in sorted(root.glob("*.md")):
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            continue
        title = text.splitlines()[0].lstrip("# ").strip() or path.stem
        docs.append({"doc_id": path.stem, "title": title, "body": text})
    return docs


def ensure_index(es: Elasticsearch, embed_fn) -> int:
    n_existing = 0
    if es.indices.exists(index=INDEX):
        n_existing = int(es.count(index=INDEX).get("count", 0))

    corpus_docs = load_markdown_docs(CORPUS_DIR)
    if corpus_docs and n_existing < len(corpus_docs) // 2:
        if es.indices.exists(index=INDEX):
            es.indices.delete(index=INDEX)
        es.indices.create(index=INDEX, mappings=index_mapping())
        actions = []
        for doc in corpus_docs:
            vec = embed_fn(f"{doc['title']}\n{doc['body'][:1200]}")
            actions.append(
                {
                    "_index": INDEX,
                    "_id": doc["doc_id"],
                    "_source": {**doc, "embedding": vec},
                }
            )
        bulk(es, actions)
        es.indices.refresh(index=INDEX)
        return len(actions)

    if not es.indices.exists(index=INDEX):
        es.indices.create(index=INDEX, mappings=index_mapping())
        seed = {
            "doc_id": "agri_seed_001",
            "title": "Норми висіву пшениці",
            "body": "Рекомендована норма висіву озимої пшениці 4–5 млн насінин на гектар.",
            "embedding": embed_fn("норма висіву пшениці"),
        }
        es.index(index=INDEX, id=seed["doc_id"], document=seed)
        es.indices.refresh(index=INDEX)
        return 1
    return n_existing