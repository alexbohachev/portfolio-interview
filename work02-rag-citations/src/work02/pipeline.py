from __future__ import annotations

import json
import time
from typing import Any

import yaml

from work02.corpus import chunk_documents, corpus_fingerprint, load_bundled_corpus
from work02.eval import evaluate_split
from work02.paths import ARTIFACTS, CONFIG, CORPUS_DIR, GOLDEN, REPORT
from work02.retrieve import HybridRetriever


def run_all() -> dict[str, Any]:
    t0 = time.perf_counter()
    with CONFIG.open(encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    docs = load_bundled_corpus(CORPUS_DIR)
    if len(docs) < cfg["corpus"]["min_docs"]:
        raise RuntimeError(f"Потрібно ≥{cfg['corpus']['min_docs']} docs; є {len(docs)}. Запустіть scripts/seed_corpus.py")

    docs_by_id = {d.doc_id: d for d in docs}
    chunks = chunk_documents(docs, cfg["corpus"]["chunk_size"], cfg["corpus"]["chunk_overlap"])
    retriever = HybridRetriever(
        [c.chunk_id for c in chunks],
        [c.doc_id for c in chunks],
        [c.text for c in chunks],
        [c.char_start for c in chunks],
        [c.char_end for c in chunks],
        cfg["retrieval"]["dense_model"],
        cfg["retrieval"]["rrf_k"],
    )

    with GOLDEN.open(encoding="utf-8") as f:
        golden = json.load(f)
    ratio = cfg["golden"]["dev_ratio"]
    split_i = int(len(golden) * ratio)
    dev, test = golden[:split_i], golden[split_i:]
    k = cfg["evaluation"]["recall_at"]

    base_dev = evaluate_split(retriever, docs_by_id, dev, "bm25", k)
    base_test = evaluate_split(retriever, docs_by_id, test, "bm25", k)
    cand_dev = evaluate_split(retriever, docs_by_id, dev, "hybrid", k)
    cand_test = evaluate_split(retriever, docs_by_id, test, "hybrid", k)

    results = {
        "corpus_fingerprint": corpus_fingerprint(docs),
        "n_docs": len(docs),
        "n_chunks": len(chunks),
        "baseline": {"dev": base_dev, "test": base_test},
        "candidate": {"dev": cand_dev, "test": cand_test},
        "elapsed_sec": round(time.perf_counter() - t0, 2),
    }

    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    (ARTIFACTS / "results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    _write_report(results, cfg)
    return results


def _write_report(results: dict[str, Any], cfg: dict[str, Any]) -> None:
    b, c = results["baseline"]["test"], results["candidate"]["test"]
    lines = [
        "# Звіт — робота 2: RAG із цитатами (retrieval MVP)",
        "",
        "## Задача",
        "Порівняння BM25 (baseline) і hybrid BM25+dense з RRF (candidate) за Recall@5 для evidence spans.",
        "",
        "## Корпус",
        f"- документів: {results['n_docs']}, chunks: {results['n_chunks']}",
        f"- fingerprint: `{results['corpus_fingerprint']}`",
        "",
        "## Результати test",
        "",
        "| Система | Recall@5 | n |",
        f"| baseline (BM25) | {b['recall_at_k']:.4f} | {b['n']} |",
        f"| candidate (hybrid) | {c['recall_at_k']:.4f} | {c['n']} |",
        "",
        "## Обмеження",
        "- Offline retrieval only; LLM-відповіді (`llm.enabled`) — наступний крок.",
        "- Synthetic golden set 60 питань; масштабування до 100 з ручною розміткою.",
        "",
        "## Наступний крок",
        "- Підключити LLM + citation judge; розширити корпус до 200–500 відкритих агро-текстів.",
        "",
        f"_Час: {results['elapsed_sec']} с._",
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")