import streamlit as st
from groq import Groq
from online_search import web_search

st.title("My Personal Web Agent")

# Get API keys from the user
groq_api_key = st.text_input(
    "Groq API Key",
    type="password",
    placeholder="Enter your Groq API key"
)

tavily_api_key = st.text_input(
    "Tavily API Key",
    type="password",
    placeholder="Enter your Tavily API key"
)

if not groq_api_key or not tavily_api_key:
    st.info("Enter both API keys to start chatting.")
    st.stop()


client = Groq(api_key=groq_api_key)
# client = Groq(api_key="YOURAPI-KEY-HERE")

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

    ## adding new content here
    search_results = web_search(prompt,tavily_api_key)
    messages = [
      {"role": m["role"], "content": m["content"]}
      for m in st.session_state.messages
  ]

    messages.append({
        "role": "system",
        "content": f"Use these web search results to answer the user:\n{search_results}"
    })

    # Get complete response from Groq
    with st.chat_message("assistant"):

        completion = client.chat.completions.create(
            model=st.session_state["groq_model"],
            messages=messages
        )

        response = completion.choices[0].message.content

        st.markdown(response)

    # Store assistant response
    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })
