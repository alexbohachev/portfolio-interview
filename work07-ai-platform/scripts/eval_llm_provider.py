"""Оцінка одного LLM-провайдера (OpenAI): цитати на dev (до 30 питань)."""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "data" / "golden" / "dev.json"
RAG_URL = os.getenv("RAG_API_URL", "http://localhost:8090").rstrip("/")
MAX_N = int(os.getenv("LLM_EVAL_N", "30"))
OUT = ROOT / "artifacts" / "llm_eval_results.json"


def post_qa(question: str) -> dict:
    payload = json.dumps({"query": question, "topK": 5}).encode("utf-8")
    req = urllib.request.Request(
        f"{RAG_URL}/v1/knowledge/qa",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read().decode())


def citation_hits(item: dict, qa: dict) -> bool:
    if qa.get("refused"):
        return not item.get("answerable", True)
    expected = {e["doc_id"] for e in item.get("evidence", []) if e.get("doc_id")}
    if not expected:
        return False
    cited = {c.get("doc_id") for c in qa.get("citations") or [] if c.get("doc_id")}
    return bool(expected & cited)


def main() -> int:
    if not os.getenv("OPENAI_API_KEY"):
        print("SKIP: OPENAI_API_KEY not set (ТЗ: оцінка провайдера офлайн без ключа)", file=sys.stderr)
        return 0
    if not GOLDEN.is_file():
        print(f"FAIL: missing {GOLDEN}", file=sys.stderr)
        return 1
    items = json.loads(GOLDEN.read_text(encoding="utf-8"))
    answerable = [q for q in items if q.get("answerable") and q.get("evidence")][:MAX_N]
    ok = 0
    rows = []
    for item in answerable:
        qa = post_qa(item["question"])
        good = citation_hits(item, qa)
        ok += int(good)
        rows.append(
            {
                "id": item.get("id"),
                "mode": qa.get("mode"),
                "citation_ok": good,
                "refused": qa.get("refused"),
            }
        )
    result = {
        "provider": "openai",
        "model_env": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        "n_evaluated": len(answerable),
        "citation_accuracy": ok / len(answerable) if answerable else 0.0,
        "citation_ok": ok,
        "samples": rows,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())