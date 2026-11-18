"""Golden 150 для work07: dev 100 (work02 dev+test, регресія) + test 50 (нові)."""
from __future__ import annotations

import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO = ROOT.parent
WORK02_G = PORTFOLIO / "work02-rag-citations" / "data" / "golden"
CORPUS = PORTFOLIO / "work02-rag-citations" / "corpus" / "bundled"
OUT_DEV = ROOT / "data" / "golden" / "dev.json"
OUT_TEST = ROOT / "data" / "golden" / "test.json"

random.seed(71)


def _single_from_md(path: Path) -> dict:
    text = path.read_text(encoding="utf-8").strip()
    doc_id = path.stem
    m = re.search(r"«([^»]+)»", text)
    expected = m.group(1) if m else ""
    span_start = text.find("Унікальне речення")
    span_end = text.find("».", span_start) + 2 if span_start >= 0 else len(text)
    return {
        "question": f"Що впливає на урожай згідно з документом {doc_id}?",
        "type": "single_doc",
        "answerable": True,
        "expected_contains": expected[:40] if expected else "",
        "evidence": [{"doc_id": doc_id, "char_start": span_start, "char_end": span_end}],
        "provenance": "work07_new",
    }


def tag(split: list[dict], prefix: str) -> list[dict]:
    out = []
    for i, q in enumerate(split):
        row = dict(q)
        row["id"] = f"{prefix}_{i + 1:03d}"
        out.append(row)
    return out


def main() -> None:
    if not WORK02_G.is_dir() or not CORPUS.is_dir():
        print("FAIL: need work02 golden + corpus", file=sys.stderr)
        raise SystemExit(1)

    w02_dev = json.loads((WORK02_G / "dev.json").read_text(encoding="utf-8"))
    w02_test = json.loads((WORK02_G / "test.json").read_text(encoding="utf-8"))
    dev_rows: list[dict] = []
    for src, part in ((w02_dev, "work02_dev"), (w02_test, "work02_test")):
        for q in src:
            row = dict(q)
            row["provenance"] = part
            dev_rows.append(row)

    used_docs: set[str] = set()
    for q in dev_rows:
        for e in q.get("evidence", []):
            if e.get("doc_id"):
                used_docs.add(e["doc_id"])

    candidates = sorted(p for p in CORPUS.glob("*.md") if p.stem not in used_docs)
    random.shuffle(candidates)
    new_test = [_single_from_md(p) for p in candidates[:50]]
    if len(new_test) < 50:
        print(f"WARN: only {len(new_test)} new test questions", file=sys.stderr)

    dev = tag(dev_rows, "w07_dev")
    test = tag(new_test, "w07_test")

    OUT_DEV.parent.mkdir(parents=True, exist_ok=True)
    OUT_DEV.write_text(json.dumps(dev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_TEST.write_text(json.dumps(test, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"dev={len(dev)} test={len(test)} total={len(dev) + len(test)}")


if __name__ == "__main__":
    main()