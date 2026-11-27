"""
v1 Streamlit app: mock login + chat on top of the RAG-only graph.

Run from the project root:
    uv run streamlit run v1_rag_only/app.py
"""
import sys
from pathlib import Path

# Streamlit only puts THIS folder on the import path. We add the project root
# so that `from common...` works.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st

from common.kb import label
from common.users import login_gate, sidebar_user
from graph import graph

st.set_page_config(page_title="Contract Assistant v1", page_icon="⚖️")

user = login_gate()
sidebar_user(user)

st.title("Contract Assistant, v1 (RAG only)")
st.caption("Answers come from contract text only. Try the clause questions, then try a dates question.")

st.session_state.setdefault("messages", [])
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if m.get("passages"):
            with st.expander("Passages used"):
                for p in m["passages"]:
                    st.markdown(f"**{label(p)}**")
                    st.text(p["text"])

if question := st.chat_input("Ask about your client's contracts"):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Searching the contracts..."):
                result = graph.invoke({"question": question, "client_id": user["client_id"]})
            st.markdown(result["answer"])
            with st.expander("Passages used"):
                for p in result["passages"]:
                    st.markdown(f"**{label(p)}**")
                    st.text(p["text"])
            st.session_state.messages.append(
                {"role": "assistant", "content": result["answer"], "passages": result["passages"]})
        except Exception as exc:  # most first-run problems are AWS setup: show them plainly
            st.error(f"Something went wrong: {exc}")
