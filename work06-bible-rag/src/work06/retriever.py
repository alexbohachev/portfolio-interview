from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from work06.config import load_config
from work06.paths import CONFIG, ROOT


@dataclass(frozen=True)
class VerseHit:
    osis_id: str
    text: str
    translation_id: str
    score: float


class BibleRetriever:
    def __init__(self, cfg: dict[str, Any] | None = None) -> None:
        self.cfg = cfg or load_config(CONFIG)
        self.db_path = ROOT / self.cfg["db_path"]
        self.index_path = ROOT / self.cfg["faiss_index"]
        self.map_path = self.index_path.with_name("faiss_map.json")
        self.model_name = self.cfg.get("embed_model", "intfloat/multilingual-e5-small")
        self.default_translation = self.cfg.get("default_translation", "uk_ubk_stub")
        self.corpus_version = self.cfg.get("corpus_version", "synthetic-mvp-1")
        self._model: SentenceTransformer | None = None
        self._index: faiss.Index | None = None
        self._ids: list[str] | None = None

    def _ensure_index(self) -> None:
        if self._index is not None:
            return
        if not self.index_path.is_file() or not self.map_path.is_file():
            raise FileNotFoundError("FAISS index missing — run .\\make.ps1 index")
        self._index = faiss.read_index(str(self.index_path))
        self._ids = json.loads(self.map_path.read_text(encoding="utf-8"))

    def _ensure_model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def verse_text(self, osis_id: str, translation_id: str | None = None) -> str | None:
        tr = translation_id or self.default_translation
        con = sqlite3.connect(self.db_path)
        row = con.execute(
            "SELECT text FROM verses WHERE osis_id=? AND translation_id=? AND corpus_version=?",
            (osis_id, tr, self.corpus_version),
        ).fetchone()
        con.close()
        return row[0] if row else None

    def search(self, question: str, top_k: int = 5, translation_id: str | None = None) -> list[VerseHit]:
        self._ensure_index()
        assert self._index is not None and self._ids is not None
        tr = translation_id or self.default_translation
        model = self._ensure_model()
        vec = model.encode("query: " + question.strip(), normalize_embeddings=True).astype(np.float32)
        scores, idx = self._index.search(vec.reshape(1, -1), top_k)
        hits: list[VerseHit] = []
        for pos, score in zip(idx[0], scores[0], strict=True):
            if pos < 0:
                continue
            osis = self._ids[pos]
            text = self.verse_text(osis, tr) or ""
            hits.append(VerseHit(osis_id=osis, text=text, translation_id=tr, score=float(score)))
        return hits


@lru_cache(maxsize=1)
def get_retriever() -> BibleRetriever:
    return BibleRetriever()