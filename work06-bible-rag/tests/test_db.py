import sqlite3
from pathlib import Path


def test_sqlite_has_90_verses():
    db = Path(__file__).resolve().parents[1] / "data" / "bible.sqlite"
    if not db.is_file():
        import pytest

        pytest.skip("run make.ps1 seed")
    n = sqlite3.connect(db).execute("SELECT COUNT(*) FROM verses").fetchone()[0]
    assert n == 90