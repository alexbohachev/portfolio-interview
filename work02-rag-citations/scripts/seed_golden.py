"""Генерує golden set (60 Q) з унікальних речень корпусу — для MVP / dev+test."""
from __future__ import annotations

import json
import re
from pathlib import Path

from work02.corpus import load_bundled_corpus

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "data" / "golden" / "questions.json"


def main() -> None:
    docs = load_bundled_corpus(ROOT / "corpus" / "bundled")
    pattern = re.compile(r"Унікальне речення для пошуку (agri_\d+_[^:]+):")
    questions = []
    for doc in docs:
        m = pattern.search(doc.text)
        if not m:
            continue
        doc_id = m.group(1).split(":")[0]
        if doc.doc_id != doc_id and doc.doc_id != m.group(1):
            doc_id = doc.doc_id
        span_start = doc.text.find("Унікальне речення")
        span_end = doc.text.find("».", span_start) + 2
        questions.append(
            {
                "id": f"q_{len(questions)+1:03d}",
                "question": f"Який фактор впливає на урожай згідно {doc.doc_id}?",
                "type": "single_doc",
                "answerable": True,
                "evidence": [{"doc_id": doc.doc_id, "char_start": span_start, "char_end": span_end}],
            }
        )
    # unanswerable
    for i in range(6):
        questions.append(
            {
                "id": f"q_unans_{i+1}",
                "question": f"Чи використовують віноградники на Марсі у 2035?",
                "type": "unanswerable",
                "answerable": False,
                "evidence": [],
            }
        )
    # multi-hop (2 docs) — synthetic
    for i in range(0, min(12, len(docs) - 1), 2):
        d1, d2 = docs[i], docs[i + 1]
        questions.append(
            {
                "id": f"q_multi_{i//2+1}",
                "question": f"Порівняй {d1.title[:20]} та {d2.title[:20]}",
                "type": "multi_hop",
                "answerable": True,
                "evidence": [
                    {"doc_id": d1.doc_id, "char_start": 0, "char_end": min(200, len(d1.text))},
                    {"doc_id": d2.doc_id, "char_start": 0, "char_end": min(200, len(d2.text))},
                ],
            }
        )
    GOLDEN.parent.mkdir(parents=True, exist_ok=True)
    GOLDEN.write_text(json.dumps(questions, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"golden questions: {len(questions)} -> {GOLDEN}")


if __name__ == "__main__":
    import sys

    sys.path.insert(0, str(ROOT / "src"))
    main()