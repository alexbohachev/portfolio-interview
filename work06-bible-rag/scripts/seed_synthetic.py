"""30 віршів × 3 «переклади» для offline MVP."""
from __future__ import annotations

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "bible.sqlite"
VERSION = "synthetic-mvp-1"
TRANSLATIONS = ("uk_ubk_stub", "uk_rb95_stub", "en_kjv_stub")


def main() -> None:
    con = sqlite3.connect(DB)
    rows = []
    for i in range(1, 31):
        osis = f"Gen.1.{i}"
        base = f"Синтетичний вірш {i} про творіння."
        for j, tr in enumerate(TRANSLATIONS):
            text = base if j == 0 else f"[{tr}] verse {i} creation token {j}"
            rows.append((osis, tr, VERSION, "Gen", 1, i, text))
    con.executemany(
        "INSERT OR REPLACE INTO verses (osis_id, translation_id, corpus_version, book, chapter, verse, text) VALUES (?,?,?,?,?,?,?)",
        rows,
    )
    con.commit()
    n = con.execute("SELECT COUNT(*) FROM verses").fetchone()[0]
    con.close()
    print(f"seeded rows={n}")


if __name__ == "__main__":
    main()