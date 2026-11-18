from __future__ import annotations

import os
from typing import Any

from work06.retriever import VerseHit


def extractive_answer(question: str, hits: list[VerseHit]) -> str:
    if not hits:
        return "Немає релевантних віршів у локальному корпусі (перевірте індекс або запит)."
    parts = [f"Запит: {question.strip()}", "", "На основі знайдених віршів:"]
    for h in hits[:3]:
        snippet = h.text[:280].replace("\n", " ")
        parts.append(f"• {h.osis_id} ({h.translation_id}): {snippet}")
    return "\n".join(parts)


def maybe_llm_answer(question: str, hits: list[VerseHit], llm_cfg: dict[str, Any]) -> str | None:
    enabled = llm_cfg.get("enabled", False) or os.getenv("WORK06_USE_LLM", "").lower() in ("1", "true", "yes")
    if not enabled or not hits:
        return None
    model_id = llm_cfg.get("model", "Qwen/Qwen2.5-0.5B-Instruct")
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError:
        return None
    ctx = "\n".join(f"[{h.osis_id}] {h.text[:200]}" for h in hits[:3])
    prompt = (
        "Ти допомагаєш відповісти лише на основі цитованих віршів. "
        "Якщо відповіді немає в тексті — скажи про це.\n\n"
        f"Вірші:\n{ctx}\n\nПитання: {question}\nВідповідь:"
    )
    try:
        tok = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            trust_remote_code=True,
            torch_dtype=torch.float32,
            device_map="cpu",
        )
        inputs = tok(prompt, return_tensors="pt")
        out = model.generate(**inputs, max_new_tokens=int(llm_cfg.get("max_new_tokens", 120)))
        text = tok.decode(out[0], skip_special_tokens=True)
        if "Відповідь:" in text:
            text = text.split("Відповідь:", 1)[-1].strip()
        return text[:800]
    except Exception:
        return None


def compose_answer(question: str, hits: list[VerseHit], cfg: dict[str, Any], use_llm: bool) -> tuple[str, str]:
    llm_cfg = {**cfg.get("llm", {}), **({"enabled": True} if use_llm else {})}
    llm_text = maybe_llm_answer(question, hits, llm_cfg)
    if llm_text:
        return llm_text, "llm"
    return extractive_answer(question, hits), "extractive"