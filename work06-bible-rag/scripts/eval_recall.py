"""Recall@5 на golden (якщо є)."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "data" / "golden" / "test.json"
INDEX = ROOT / "artifacts" / "faiss.index"
MAP = ROOT / "artifacts" / "faiss_map.json"
MODEL = "intfloat/multilingual-e5-small"
TOP_K = 5


def main() -> int:
    if not GOLDEN.is_file():
        print("skip: no golden")
        return 0
    items = json.loads(GOLDEN.read_text(encoding="utf-8"))
    index = faiss.read_index(str(INDEX))
    ids = json.loads(MAP.read_text(encoding="utf-8"))
    model = SentenceTransformer(MODEL)
    hit = 0
    n = 0
    for q in items:
        expected = set(q.get("osis_ids", []))
        if not expected:
            continue
        n += 1
        vec = model.encode("query: " + q["question"], normalize_embeddings=True).astype(np.float32)
        scores, idx = index.search(vec.reshape(1, -1), TOP_K)
        got = {ids[i] for i in idx[0] if i >= 0}
        if expected & got:
            hit += 1
    rate = hit / n if n else 0.0
    print(json.dumps({"recall_at_5": rate, "n": n}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())