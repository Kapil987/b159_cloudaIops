import streamlit as st
from groq import Groq

st.title("ChatGPT-like clone")

client = Groq(api_key="YourAPIKeyHere")

if "groq_model" not in st.session_state:
    st.session_state["groq_model"] = "openai/gpt-oss-20b"

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("What is up?"):

    # Store user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # Get complete response from Groq
    with st.chat_message("assistant"):

        completion = client.chat.completions.create(
            model=st.session_state["groq_model"],
            messages=st.session_state.messages
        )

        response = completion.choices[0].message.content

        st.markdown(response)

    # Store assistant response
    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })
