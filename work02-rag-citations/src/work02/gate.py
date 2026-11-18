from __future__ import annotations

from typing import Any

import numpy as np

from work02.retrieve import HybridRetriever


def max_retrieval_score(retriever: HybridRetriever, query: str, k: int) -> float:
    hits = retriever.search_hybrid(query, k)
    if not hits:
        return 0.0
    return float(hits[0].score)


def tune_refusal_threshold(
    retriever: HybridRetriever,
    dev: list[dict[str, Any]],
    k: int,
    grid: np.ndarray | None = None,
) -> tuple[float, dict[str, float]]:
    if grid is None:
        grid = np.linspace(0.001, 0.15, 60)
    scores: list[tuple[float, bool]] = []
    for q in dev:
        s = max_retrieval_score(retriever, q["question"], k)
        scores.append((s, bool(q.get("answerable", True))))

    unans_scores = [s for s, a in scores if not a]
    if unans_scores:
        floor_t = float(max(unans_scores) + 1e-6)
    else:
        floor_t = float(grid[0])

    best_t = floor_t
    best_f1 = -1.0
    for t in grid:
        if t < floor_t:
            continue
        tp = fp = fn = tn = 0
        for s, answerable in scores:
            refuse = s < t
            if not answerable and refuse:
                tn += 1
            elif not answerable and not refuse:
                fp += 1
            elif answerable and not refuse:
                tp += 1
            else:
                fn += 1
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
        if f1 > best_f1:
            best_f1 = f1
            best_t = float(t)
    return best_t, {"dev_gate_f1": best_f1}