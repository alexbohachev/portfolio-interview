from __future__ import annotations

import os
import re
from dataclasses import dataclass

from elasticsearch import Elasticsearch
from openai import OpenAI

from app.config import OPENAI_MODEL, REFUSAL
from app.retrieve import Hit, search_hybrid


@dataclass
class Citation:
    doc_id: str
    excerpt: str
    char_start: int
    char_end: int


@dataclass
class QaResult:
    answer: str
    refused: bool
    citations: list[Citation]
    mode: str


def _extractive(hits: list[Hit]) -> str:
    if not hits:
        return REFUSAL
    text = hits[0].snippet
    m = re.search(r"«([^»]+)»", text)
    if m:
        return m.group(1).strip()
    m2 = re.search(r"фактор «([^»]+)»", text)
    if m2:
        return f"Критичний фактор: {m2.group(1)}"
    return text.split("\n")[0][:280]


def _openai_answer(query: str, hits: list[Hit]) -> str:
    client = OpenAI()
    context = "\n\n".join(f"[{h.doc_id}] {h.snippet}" for h in hits[:3])
    msg = client.chat.completions.create(
        model=OPENAI_MODEL,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": "Відповідай українською лише з контексту. Якщо відповіді немає — "
                f"скажи дослівно: «{REFUSAL}»",
            },
            {"role": "user", "content": f"Контекст:\n{context}\n\nПитання: {query}"},
        ],
    )
    return msg.choices[0].message.content.strip()


def _citations(hits: list[Hit]) -> list[Citation]:
    cites: list[Citation] = []
    for h in hits[:2]:
        start = max(h.snippet.find("«"), 0)
        end = h.snippet.find("»", start) + 1 if "»" in h.snippet else min(len(h.snippet), 200)
        cites.append(Citation(doc_id=h.doc_id, excerpt=h.snippet[:200], char_start=start, char_end=end))
    return cites


def answer_query(
    es: Elasticsearch,
    embed_fn,
    query: str,
    top_k: int = 5,
) -> QaResult:
    vector = embed_fn(query)
    hits = search_hybrid(es, query, vector, top_k)
    if not hits:
        return QaResult(answer=REFUSAL, refused=True, citations=[], mode="gate")

    if os.environ.get("OPENAI_API_KEY"):
        text = _openai_answer(query, hits)
        refused = REFUSAL.split()[0] in text
        return QaResult(
            answer=text,
            refused=refused,
            citations=[] if refused else _citations(hits),
            mode="openai",
        )

    return QaResult(
        answer=_extractive(hits),
        refused=False,
        citations=_citations(hits),
        mode="extractive",
    )