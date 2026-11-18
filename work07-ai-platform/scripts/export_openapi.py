"""Завантажує openapi.json з rag-api у openapi/rag-api.openapi.json."""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path

RAG_URL = os.getenv("RAG_API_URL", "http://localhost:8090").rstrip("/")
OUT = Path(__file__).resolve().parents[1] / "openapi" / "rag-api.openapi.json"


def main() -> int:
    try:
        with urllib.request.urlopen(f"{RAG_URL}/openapi.json", timeout=30) as r:
            spec = json.loads(r.read().decode())
    except OSError as exc:
        print(f"SKIP/FAIL: rag-api not reachable: {exc}", file=sys.stderr)
        return 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"written {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())