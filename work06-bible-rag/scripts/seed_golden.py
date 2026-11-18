"""30 golden (dev/test 15) для synthetic MVP."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEV = ROOT / "data" / "golden" / "dev.json"
TEST = ROOT / "data" / "golden" / "test.json"


def row(i: int, split: str) -> dict:
    osis = f"Gen.1.{i}"
    return {
        "id": f"{split}_{i:03d}",
        "question": f"Що говорить вірш {osis} про творіння?",
        "osis_ids": [osis],
        "category": "paraphrase_uk",
    }


def main() -> None:
    dev = [row(i, "dev") for i in range(1, 16)]
    test = [row(i, "test") for i in range(16, 31)]
    DEV.parent.mkdir(parents=True, exist_ok=True)
    DEV.write_text(json.dumps(dev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    TEST.write_text(json.dumps(test, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"dev={len(dev)} test={len(test)}")


if __name__ == "__main__":
    main()