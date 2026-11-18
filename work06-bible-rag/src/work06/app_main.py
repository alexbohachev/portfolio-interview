from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

from work06.config import load_config
from work06.generate import compose_answer
from work06.paths import CONFIG
from work06.retriever import get_retriever

app = FastAPI(title="work06-bible-rag", version="0.2.0")
_cfg = load_config(CONFIG)


class AskRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=10)
    translation_id: str | None = None
    use_llm: bool = False


@app.get("/health")
def health() -> dict[str, Any]:
    r = get_retriever()
    ok_index = r.index_path.is_file()
    return {
        "status": "ok",
        "corpus_version": r.corpus_version,
        "index_ready": ok_index,
        "default_translation": r.default_translation,
    }


@app.post("/v1/ask")
def ask(body: AskRequest) -> dict[str, Any]:
    retriever = get_retriever()
    hits = retriever.search(body.question, top_k=body.top_k, translation_id=body.translation_id)
    answer, mode = compose_answer(body.question, hits, _cfg, body.use_llm)
    return {
        "question": body.question,
        "answer": answer,
        "mode": mode,
        "citations": [
            {"osis_id": h.osis_id, "translation_id": h.translation_id, "score": h.score, "text": h.text}
            for h in hits
        ],
    }