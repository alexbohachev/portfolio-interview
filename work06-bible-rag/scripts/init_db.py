"""SQLite схема віршів (work06)."""
from __future__ import annotations

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "bible.sqlite"

SCHEMA = """
CREATE TABLE IF NOT EXISTS verses (
  osis_id TEXT NOT NULL,
  translation_id TEXT NOT NULL,
  corpus_version TEXT NOT NULL,
  book TEXT NOT NULL,
  chapter INTEGER NOT NULL,
  verse INTEGER NOT NULL,
  text TEXT NOT NULL,
  PRIMARY KEY (osis_id, translation_id, corpus_version)
);
CREATE INDEX IF NOT EXISTS idx_verses_tr ON verses(translation_id, corpus_version);
"""


def main() -> None:
    DB.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB)
    con.executescript(SCHEMA)
    con.commit()
    con.close()
    print(f"init {DB}")


if __name__ == "__main__":
    main()