"""
Mock login for the course. No passwords, no real identity provider.

The point of this file: the app learns WHICH CLIENT the attorney is working for
from the login, and nothing else. That client_id is passed into the graph and
added by CODE to every Knowledge Base search and every SQL query. The LLM never
sees it and can never change it. That is how Nova's contracts stay invisible
to Greenfield's attorney, even if the model makes a mistake.
"""
import streamlit as st

FAKE_USERS = {
    "priya": {"name": "Priya Sharma (Sharma & Co, Nova Foods team)", "client_id": "nova_foods"},
    "arjun": {"name": "Arjun Mehta (Sharma & Co, Greenfield Retail team)", "client_id": "greenfield_retail"},
}


def login_gate() -> dict:
    """Show a mock login until someone picks a user. Returns the logged-in user."""
    if "user" not in st.session_state:
        st.title("Sharma & Co: Contract Assistant")
        st.caption("Mock login for the course. Pick an attorney, no password needed.")
        username = st.selectbox("Attorney", list(FAKE_USERS), format_func=lambda u: FAKE_USERS[u]["name"])
        if st.button("Log in"):
            st.session_state["user"] = {"username": username, **FAKE_USERS[username]}
            st.rerun()
        st.stop()  # nothing below this runs until a user is logged in
    return st.session_state["user"]


def sidebar_user(user: dict) -> None:
    """Show who is logged in, with a log out button."""
    with st.sidebar:
        st.write(f"Logged in as **{user['name']}**")
        st.caption(f"client_id: `{user['client_id']}`")
        if st.button("Log out"):
            st.session_state.clear()
            st.rerun()
