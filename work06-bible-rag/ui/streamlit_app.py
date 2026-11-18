"""Streamlit UI — work06 Bible RAG."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import streamlit as st

from work06.config import load_config
from work06.generate import compose_answer
from work06.paths import CONFIG
from work06.retriever import BibleRetriever

st.set_page_config(page_title="Bible RAG (work06)", layout="wide")
st.title("Локальний Bible RAG")
st.caption("Retrieval: multilingual-e5 + FAISS · відповідь extractive (LLM — опційно)")

cfg = load_config(CONFIG)
translations = cfg.get("translations", ["uk_ubk_stub", "uk_rb95_stub", "en_kjv_stub"])

with st.sidebar:
    tr = st.selectbox("Переклад", translations, index=0)
    top_k = st.slider("Top-K", 1, 10, 5)
    use_llm = st.checkbox("LLM (потрібен transformers + WORK06_USE_LLM)", value=False)

question = st.text_input("Питання", placeholder="Що говорить вірш Gen.1.1 про творіння?")

if st.button("Запитати", type="primary") and question.strip():
    try:
        retriever = BibleRetriever(cfg)
        hits = retriever.search(question.strip(), top_k=top_k, translation_id=tr)
        answer, mode = compose_answer(question.strip(), hits, cfg, use_llm)
        st.subheader("Відповідь")
        st.info(f"Режим: **{mode}**")
        st.write(answer)
        st.subheader("Цитати")
        for h in hits:
            st.markdown(f"**{h.osis_id}** ({h.translation_id}) · score {h.score:.3f}")
            st.write(h.text)
    except FileNotFoundError as e:
        st.error(str(e))