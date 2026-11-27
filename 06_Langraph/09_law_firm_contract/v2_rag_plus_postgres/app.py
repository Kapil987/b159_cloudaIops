"""
v2 Streamlit app: mock login + chat on top of the router / Postgres / RAG graph.

Run from the project root:
    uv run streamlit run v2_rag_plus_postgres/app.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st

from common.config import AS_OF_DATE
from common.kb import label
from common.users import login_gate, sidebar_user
from graph import graph

st.set_page_config(page_title="Contract Assistant v2", page_icon="⚖️")

user = login_gate()
sidebar_user(user)


def show_trace(trace: dict) -> None:
    """The 'how was this answer built' panel, so students can see each agent's part."""
    with st.expander("How this answer was built"):
        st.write(f"**Router chose:** `{trace['route']}`")
        if trace.get("tool_call"):
            st.write(f"**Postgres query:** `{trace['tool_call']['tool']}` {trace['tool_call']}")
        if trace.get("contracts"):
            st.write("**Facts from Postgres**")
            st.dataframe(trace["contracts"], hide_index=True)
        if trace.get("passages"):
            st.write("**Passages from the Knowledge Base**")
            for p in trace["passages"]:
                st.markdown(f"*{label(p)}*")
                st.text(p["text"])


st.title("Contract Assistant, v2 (RAG + Postgres)")
st.caption(f"Today's date in this demo: {AS_OF_DATE:%d %b %Y}. "
           "Try: contracts expiring in 90 days, a clause question, then a question that needs both.")

st.session_state.setdefault("messages", [])
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if m.get("trace"):
            show_trace(m["trace"])

if question := st.chat_input("Ask about your client's contracts"):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Working on it..."):
                result = graph.invoke({"question": question, "client_id": user["client_id"]})
            st.markdown(result["answer"])
            trace = {k: result.get(k) for k in ("route", "tool_call", "contracts", "passages")}
            show_trace(trace)
            st.session_state.messages.append({"role": "assistant", "content": result["answer"], "trace": trace})
        except Exception as exc:  # most first-run problems are AWS or Postgres setup: show them plainly
            st.error(f"Something went wrong: {exc}")
