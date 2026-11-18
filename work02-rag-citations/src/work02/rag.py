from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any

from work02.retrieve import HybridRetriever, RankedHit

REFUSAL = "Немає достатньо даних у корпусі для відповіді."


@dataclass
class RagAnswer:
    text: str
    refused: bool
    citations: list[dict[str, Any]]


def _extractive_answer(hit: RankedHit) -> str:
    m = re.search(r"«([^»]+)»", hit.text)
    if m:
        return m.group(1).strip()
    sentences = re.split(r"(?<=[.!?])\s+", hit.text.strip())
    return sentences[0][:280] if sentences else hit.text[:280]


def _openai_answer(question: str, hits: list[RankedHit], model: str) -> str:
    import requests

    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY не задано")
    context = "\n\n".join(f"[{h.doc_id}] {h.text[:500]}" for h in hits[:3])
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "Відповідай українською лише з наданого контексту. "
                "Якщо відповіді немає, скажи: «Немає достатньо даних у корпусі для відповіді.»",
            },
            {"role": "user", "content": f"Контекст:\n{context}\n\nПитання: {question}"},
        ],
        "temperature": 0,
    }
    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json=payload,
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def answer_question(
    retriever: HybridRetriever,
    question: str,
    threshold: float,
    k: int,
    llm_cfg: dict[str, Any],
) -> RagAnswer:
    hits = retriever.search_hybrid(question, k)
    top_score = hits[0].score if hits else 0.0
    if top_score < threshold:
        return RagAnswer(REFUSAL, refused=True, citations=[])

    cites = [
        {
            "doc_id": h.doc_id,
            "chunk_id": h.chunk_id,
            "char_start": h.char_start,
            "char_end": h.char_end,
            "excerpt": h.text[:200],
        }
        for h in hits[:2]
    ]
    if llm_cfg.get("enabled") and os.environ.get("OPENAI_API_KEY"):
        text = _openai_answer(question, hits, llm_cfg["model"])
        refused = REFUSAL[:20] in text or text.strip() == REFUSAL
        return RagAnswer(text, refused=refused, citations=[] if refused else cites)

    text = _extractive_answer(hits[0])
    return RagAnswer(text, refused=False, citations=cites)