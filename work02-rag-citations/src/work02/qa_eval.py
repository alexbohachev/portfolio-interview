from __future__ import annotations

from typing import Any

from work02.corpus import Document
from work02.rag import REFUSAL, RagAnswer, answer_question
from work02.retrieve import HybridRetriever


def citation_hits_evidence(answer: RagAnswer, evidence: list[dict[str, Any]]) -> bool:
    if answer.refused or not evidence:
        return False
    for ev in evidence:
        for c in answer.citations:
            if c["doc_id"] != ev["doc_id"]:
                continue
            if not (c["char_end"] <= ev["char_start"] or c["char_start"] >= ev["char_end"]):
                return True
    return False


def evaluate_qa(
    retriever: HybridRetriever,
    docs_by_id: dict[str, Document],
    questions: list[dict[str, Any]],
    threshold: float,
    k: int,
    llm_cfg: dict[str, Any],
) -> dict[str, Any]:
    correct_refusal = 0
    refusal_n = 0
    cite_ok = 0
    cite_n = 0
    contain_ok = 0
    contain_n = 0

    for q in questions:
        ans = answer_question(retriever, q["question"], threshold, k, llm_cfg)
        if not q.get("answerable", True):
            refusal_n += 1
            if ans.refused:
                correct_refusal += 1
            continue
        if ans.refused:
            continue
        evidence = q.get("evidence", [])
        cite_n += 1
        if citation_hits_evidence(ans, evidence):
            cite_ok += 1
        expected = q.get("expected_contains")
        if expected:
            contain_n += 1
            if expected.lower() in ans.text.lower():
                contain_ok += 1

    return {
        "correct_refusals": f"{correct_refusal} / {refusal_n}" if refusal_n else "n/a",
        "citation_accuracy": f"{cite_ok} / {cite_n}" if cite_n else "n/a",
        "answer_contains_gold": f"{contain_ok} / {contain_n}" if contain_n else "n/a",
        "refusal_rate_unanswerable": correct_refusal / refusal_n if refusal_n else None,
        "citation_acc_rate": cite_ok / cite_n if cite_n else None,
    }