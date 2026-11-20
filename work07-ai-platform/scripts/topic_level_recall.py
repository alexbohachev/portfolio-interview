"""Topic-level Hit@5 from per-query eval files (did the top-5 contain ANY document of the expected topic?).

The synthetic corpus has 20 near-identical documents per topic (they differ only by a keyword and a year),
so document-level Recall@5 cannot discriminate within a topic. This separates "found the right topic"
from "guessed the right template document".

Usage: python scripts/topic_level_recall.py manifests/eval_per_query_extended.json [more files...]
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def topic(doc_id: str) -> str:
    return re.sub(r"^agri_\d+_|_\d+$", "", doc_id)


def main(paths: list[str]) -> int:
    for name in paths:
        rows = json.loads(Path(name).read_text(encoding="utf-8"))
        res = {
            k: sum(any(topic(t) == topic(e) for e in r["expected"] for t in r[f"{k}_top5"]) for r in rows) / len(rows)
            for k in ("bm25", "hybrid", "rerank")
        }
        print(f"{name} (n={len(rows)}): " + " | ".join(f"{k} {v:.3f}" for k, v in res.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
