"""FAISS dense index (E5) по uk_ubk_stub."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "bible.sqlite"
OUT = ROOT / "artifacts" / "faiss.index"
MAP = ROOT / "artifacts" / "faiss_map.json"
MODEL = "intfloat/multilingual-e5-small"
TR = "uk_ubk_stub"
VERSION = "synthetic-mvp-1"
PREFIX = "passage: "


def main() -> None:
    con = sqlite3.connect(DB)
    cur = con.execute(
        "SELECT osis_id, text FROM verses WHERE translation_id=? AND corpus_version=? ORDER BY verse",
        (TR, VERSION),
    )
    rows = cur.fetchall()
    con.close()
    if not rows:
        raise SystemExit("empty corpus — run seed_synthetic.py")
    model = SentenceTransformer(MODEL)
    texts = [PREFIX + t for _, t in rows]
    emb = model.encode(texts, normalize_embeddings=True).astype(np.float32)
    index = faiss.IndexFlatIP(emb.shape[1])
    index.add(emb)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(OUT))
    MAP.write_text(json.dumps([r[0] for r in rows], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"index {len(rows)} dim={emb.shape[1]}")


if __name__ == "__main__":
    main()