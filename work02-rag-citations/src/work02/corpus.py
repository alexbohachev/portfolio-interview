from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

DOC_SEP = "\n"


@dataclass(frozen=True)
class Document:
    doc_id: str
    title: str
    text: str

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.text.encode("utf-8")).hexdigest()


def load_bundled_corpus(directory: Path) -> list[Document]:
    docs: list[Document] = []
    for path in sorted(directory.glob("*.md")):
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            continue
        title = text.splitlines()[0].lstrip("# ").strip() or path.stem
        docs.append(Document(doc_id=path.stem, title=title, text=text))
    return docs


def corpus_fingerprint(docs: list[Document]) -> str:
    payload = json.dumps(
        [{"doc_id": d.doc_id, "sha256": d.sha256} for d in sorted(docs, key=lambda x: x.doc_id)],
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    text: str
    char_start: int
    char_end: int


def chunk_documents(
    docs: list[Document],
    chunk_size: int,
    overlap: int,
) -> list[Chunk]:
    chunks: list[Chunk] = []
    for doc in docs:
        text = doc.text
        start = 0
        idx = 0
        while start < len(text):
            end = min(len(text), start + chunk_size)
            piece = text[start:end]
            cid = f"{doc.doc_id}::c{idx}"
            chunks.append(
                Chunk(
                    chunk_id=cid,
                    doc_id=doc.doc_id,
                    text=piece,
                    char_start=start,
                    char_end=end,
                )
            )
            if end >= len(text):
                break
            start = end - overlap
            idx += 1
    return chunks