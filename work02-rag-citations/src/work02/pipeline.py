from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any

from work02.config import config_fingerprint, load_config
from work02.corpus import chunk_documents, corpus_fingerprint, load_bundled_corpus
from work02.eval import evaluate_split
from work02.gate import tune_refusal_threshold
from work02.paths import ARTIFACTS, CONFIG, CORPUS_DIR, GOLDEN_DEV, GOLDEN_TEST, MANIFEST, REPORT
from work02.qa_eval import evaluate_qa
from work02.retrieve import HybridRetriever


def _golden_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def _load_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def run_all() -> dict[str, Any]:
    t0 = time.perf_counter()
    cfg = load_config(CONFIG)
    fp = config_fingerprint(cfg)
    manifest = _load_manifest()
    locked = manifest.get("config_hash")
    if locked and locked not in ("pending_lock", "") and locked != fp:
        raise RuntimeError(f"config_hash mismatch: manifest={locked}, config={fp}. Запустіть `work02 lock`.")

    docs = load_bundled_corpus(CORPUS_DIR)
    if len(docs) < cfg["corpus"]["min_docs"]:
        raise RuntimeError(f"Потрібно ≥{cfg['corpus']['min_docs']} docs; є {len(docs)}. Запустіть `work02 seed`.")

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

    dev = json.loads(GOLDEN_DEV.read_text(encoding="utf-8"))
    test = json.loads(GOLDEN_TEST.read_text(encoding="utf-8"))
    k = cfg["evaluation"]["recall_at"]

    gate_thresh, gate_meta = tune_refusal_threshold(retriever, dev, k)

    base_test = evaluate_split(retriever, docs_by_id, test, "bm25", k)
    cand_test = evaluate_split(retriever, docs_by_id, test, "hybrid", k)
    qa_test = evaluate_qa(retriever, docs_by_id, test, gate_thresh, k, cfg["llm"])

    results = {
        "corpus_fingerprint": corpus_fingerprint(docs),
        "golden_test_sha256_16": _golden_sha(GOLDEN_TEST),
        "n_docs": len(docs),
        "n_chunks": len(chunks),
        "retrieval_gate_threshold": gate_thresh,
        "gate_tune": gate_meta,
        "baseline_retrieval_test": base_test,
        "candidate_retrieval_test": cand_test,
        "qa_test": qa_test,
        "llm_enabled": bool(cfg["llm"].get("enabled")),
        "elapsed_sec": round(time.perf_counter() - t0, 2),
    }

    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    (ARTIFACTS / "results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    _write_report(results)
    return results


def _write_report(results: dict[str, Any]) -> None:
    b, c = results["baseline_retrieval_test"], results["candidate_retrieval_test"]
    qa = results["qa_test"]
    lines = [
        "# Звіт — робота 2: RAG із цитатами",
        "",
        "## Задача",
        "Retrieval (BM25 vs hybrid RRF) + retrieval gate + відповідь з цитатами (extractive offline / LLM за ключем).",
        "",
        "## Корпус",
        f"- документів: {results['n_docs']}, fingerprint `{results['corpus_fingerprint']}`",
        f"- test golden sha: `{results['golden_test_sha256_16']}`",
        "",
        "## Retrieval (test)",
        "| Система | Recall@5 | n |",
        f"| baseline BM25 | {b['recall_at_k']:.4f} | {b['n']} |",
        f"| candidate hybrid | {c['recall_at_k']:.4f} | {c['n']} |",
        "",
        f"**Retrieval gate** (поріг max RRF на dev): `{results['retrieval_gate_threshold']:.4f}`",
        "",
        "## QA (test, candidate + gate)",
        f"- Коректні відмови: {qa['correct_refusals']}",
        f"- Точність цитат (overlap evidence): {qa['citation_accuracy']}",
        f"- Відповідь містить gold-фрагмент: {qa['answer_contains_gold']}",
        "",
        "## Обмеження",
        "- Синтетичний корпус 200 docs; LLM вимкнено за замовчуванням.",
        "- Промпт не замінює retrieval gate (відмова лише в коді за порогом).",
        "",
        "## Наступний крок",
        "- Відкритий агро-корпус 200–500 + ручний golden; LLM-judge на 30 прикладах.",
        "",
        f"_Час: {results['elapsed_sec']} с._",
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")