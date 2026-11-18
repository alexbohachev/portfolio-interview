"""Golden ~100: 60 single / 20 multi / 20 unanswerable; dev/test 50/50 за типом."""
from __future__ import annotations

import json
import random
import re
from pathlib import Path

from work02.corpus import load_bundled_corpus

ROOT = Path(__file__).resolve().parents[1]
DEV = ROOT / "data" / "golden" / "dev.json"
TEST = ROOT / "data" / "golden" / "test.json"
random.seed(42)


def _single_from_doc(doc) -> dict:
    m = re.search(r"«([^»]+)»", doc.text)
    expected = m.group(1) if m else ""
    span_start = doc.text.find("Унікальне речення")
    span_end = doc.text.find("».", span_start) + 2 if span_start >= 0 else len(doc.text)
    return {
        "question": f"Що впливає на урожай згідно з документом {doc.doc_id}?",
        "type": "single_doc",
        "answerable": True,
        "expected_contains": expected[:40] if expected else "",
        "evidence": [{"doc_id": doc.doc_id, "char_start": span_start, "char_end": span_end}],
    }


def main() -> None:
    docs = load_bundled_corpus(ROOT / "corpus" / "bundled")
    singles = [_single_from_doc(d) for d in docs]
    random.shuffle(singles)
    single_pick = singles[:60]

    multi: list[dict] = []
    for i in range(0, 40, 2):
        if len(multi) >= 20:
            break
        d1, d2 = docs[i], docs[i + 1]
        multi.append(
            {
                "question": f"Порівняй рекомендації {d1.doc_id} та {d2.doc_id}",
                "type": "multi_hop",
                "answerable": True,
                "expected_contains": "",
                "evidence": [
                    {"doc_id": d1.doc_id, "char_start": 0, "char_end": min(250, len(d1.text))},
                    {"doc_id": d2.doc_id, "char_start": 0, "char_end": min(250, len(d2.text))},
                ],
            }
        )

    unanswerable = [
        {
            "question": q,
            "type": "unanswerable",
            "answerable": False,
            "evidence": [],
        }
        for q in [
            "Чи вирощують рис на Марсі у 2040 році?",
            "Який ROI інвестицій у криптовалюту на полі?",
            "Скільки літрів оливи видобувають з одного гектара пшениці?",
            "Чи схвалив МОЗ препарат X123 для метеликів?",
            "Яка погода на Венері для посіву сої?",
            "Чи існує гібрид кукурудзи з мідним листям?",
            "Скільки кіловат батареї потрібно для фотосинтезу пшениці?",
            "Чи реєструвався агро-дрон NVIDIA H100 у ЄС?",
            "Який гербіцид заборонений на Місяці?",
            "Чи входить IoT-бджола в Держреєстр 2028?",
        ]
    ]
    unanswerable += [
        {
            "question": f"Чи існує культура «lunar_{i}» у корпусі?",
            "type": "unanswerable",
            "answerable": False,
            "evidence": [],
        }
        for i in range(10)
    ]

    all_q = single_pick + multi + unanswerable
    by_type: dict[str, list] = {}
    for q in all_q:
        by_type.setdefault(q["type"], []).append(q)

    dev, test = [], []
    for items in by_type.values():
        random.shuffle(items)
        half = len(items) // 2
        dev.extend(items[:half])
        test.extend(items[half:])

    def tag(split: list[dict], name: str) -> list[dict]:
        out = []
        for i, q in enumerate(split):
            row = dict(q)
            row["id"] = f"{name}_{i+1:03d}"
            out.append(row)
        return out

    DEV.parent.mkdir(parents=True, exist_ok=True)
    DEV.write_text(json.dumps(tag(dev, "dev"), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    TEST.write_text(json.dumps(tag(test, "test"), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"dev={len(dev)} test={len(test)} total={len(dev)+len(test)}")


if __name__ == "__main__":
    import sys

    sys.path.insert(0, str(ROOT / "src"))
    main()