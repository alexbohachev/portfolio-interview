"""Спільна логіка top-3 рекомендацій (worker + eval)."""
from __future__ import annotations

import json
import os
from pathlib import Path

DEFAULT_CATALOG = Path(__file__).resolve().parents[2] / "config" / "actions_catalog.json"


def load_catalog(path: str | None = None) -> list[dict]:
    catalog_path = Path(path or os.getenv("ACTIONS_CATALOG", str(DEFAULT_CATALOG)))
    if catalog_path.is_file():
        return json.loads(catalog_path.read_text(encoding="utf-8"))
    return [{"id": "rescout_7d", "label": "Повторний огляд поля через 7 днів"}]


def pick_actions(
    note: str,
    hits: list[dict],
    catalog: list[dict],
    top: int = 3,
) -> list[dict]:
    blob = note.lower() + " " + " ".join(h.get("snippet", "").lower() for h in hits)
    rules: list[tuple[str, tuple[str, ...]]] = [
        ("spray_fungicide", ("ірж", "фузар", "септор", "гриб", "фунгі")),
        ("ipm_scouting", ("шкід", "метелик", "феромон", "іпм", "трихограм")),
        ("adjust_irrigation", ("зрош", "краплин", "волого", "посух")),
        ("soil_lime", ("ph", "кисл", "вапн", "лімаш", "кислот")),
        ("herbicide_band", ("бур'ян", "гербіц", "буря", "буряк")),
        ("rescout_7d", ("плям", "огляд", "сумнів", "повтор")),
        ("nitrogen_topdress", ("азот", "піджив", "npk")),
        ("seed_rate_review", ("висів", "густ", "норма", "щільн")),
    ]
    scores: dict[str, int] = {a["id"]: 0 for a in catalog}
    for action_id, keys in rules:
        if action_id not in scores:
            continue
        for k in keys:
            if k in blob:
                scores[action_id] += 2
    for action in catalog:
        label = action["label"].lower()
        for token in label.split():
            if len(token) > 4 and token in blob:
                scores[action["id"]] += 1

    ranked = sorted(catalog, key=lambda a: (-scores.get(a["id"], 0), a["id"]))
    cite = hits[0] if hits else {}
    out: list[dict] = []
    seen: set[str] = set()
    for action in ranked:
        if len(out) >= top:
            break
        if scores.get(action["id"], 0) <= 0 and out:
            continue
        if action["id"] in seen:
            continue
        seen.add(action["id"])
        out.append(
            {
                "action_id": action["id"],
                "label": action["label"],
                "citation_doc_id": cite.get("doc_id", ""),
                "citation_excerpt": (cite.get("snippet") or "")[:200],
            }
        )
    if len(out) < top:
        for action in ranked:
            if len(out) >= top:
                break
            if action["id"] in seen:
                continue
            seen.add(action["id"])
            out.append(
                {
                    "action_id": action["id"],
                    "label": action["label"],
                    "citation_doc_id": cite.get("doc_id", ""),
                    "citation_excerpt": (cite.get("snippet") or "")[:200],
                }
            )
    return out[:top]