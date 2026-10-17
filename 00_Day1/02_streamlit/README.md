# Streamlit Web Agent: Groq + Tavily Search

A chat app built step by step. It starts from Streamlit's official ChatGPT-clone tutorial and ends as a web-search chatbot with streaming replies, ready to deploy on Streamlit Community Cloud.

## 0. Setup: start from raw Streamlit

Assumes a `uv` project already exists (see [`01_uv_git/01_setup.md`](../01_uv_git/01_setup.md): `uv init`, etc.). From inside that project:

1. **Get API keys**
   - Groq (free): [console.groq.com/keys](https://console.groq.com/keys)
   - Tavily (for search, from step 2 on): [app.tavily.com](https://app.tavily.com)

2. **Install the packages**
   ```bash
   uv add streamlit groq tavily-python
   ```
   This records them in `pyproject.toml`, which Streamlit Cloud can also read at deploy time.

3. **Create the app files** from the steps below, starting with `1_app.py`.


## 1. Original code (from Streamlit's official docs)

Source: docs.streamlit.io/develop/tutorials/chat-and-llm-apps/build-conversational-apps#build-a-chatgpt-like-app

```python
from openai import OpenAI
import streamlit as st

st.title("ChatGPT-like clone")
client = Groq(api_key='GROQ_API_KEY')
# client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
```

## Paste this into AI chat

```
Convert the following Python Streamlit chat application from the OpenAI SDK to the Groq SDK.

Requirements:
1. Replace `from openai import OpenAI` with `from groq import Groq`.
2. Initialize the Groq client using `Groq(api_key=st.secrets["GROQ_API_KEY"])`.
3. Rename the session state key from `openai_model` to `groq_model`.
4. Change the model from `gpt-3.5-turbo` to `openai/gpt-oss-20b`.
5. Keep the existing chat history functionality using `st.session_state.messages`.
6. Preserve the display of previous user and assistant messages using `st.chat_message()` and `st.markdown()`.
7. Keep the `st.chat_input()` prompt handling unchanged.
8. Replace streaming responses (`stream=True` and `st.write_stream()`) with a non-streaming completion request.
9. Extract the response using `completion.choices[0].message.content` and display it using `st.markdown(response)`.
10. Append the assistant response to the session state so that conversation history is maintained.
11. Remove all OpenAI-specific imports, client initialization, and session state references.
12. Keep the code simple and avoid unnecessary changes to the original application structure.

Return the complete, runnable Python code, not just a list of modifications.

**Original code:**
[Paste the first Streamlit application here]
```


## 2. Groq version — the easy way (copy-paste this one)

No streaming, no generator, no `write_stream` — just ask Groq for one
complete answer and print it. The only trade-off: the reply appears all at
once after a short pause, instead of typing itself out word-by-word. Fine
trade for Day 1.

```python
import streamlit as st
from groq import Groq                                          # CHANGED: was `from openai import OpenAI`

st.title("Groq-powered chat")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])               # CHANGED: was `OpenAI(api_key=st.secrets["OPENAI_API_KEY"])`

if "groq_model" not in st.session_state:                       # CHANGED: was `"openai_model"`
    st.session_state["groq_model"] = "openai/gpt-oss-20b"       # CHANGED: was `"gpt-3.5-turbo"`

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        completion = client.chat.completions.create(            # CHANGED: no `stream=True` at all
            model=st.session_state["groq_model"],               # CHANGED: was `st.session_state["openai_model"]`
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
        )
        response = completion.choices[0].message.content        # CHANGED: was `st.write_stream(stream)`
        st.markdown(response)                                   # NEW: print the full answer directly
    st.session_state.messages.append({"role": "assistant", "content": response})
```

4. **Keys, local vs. final app**
   - `1_app.py` and `2_app_search.py` hardcode the key (placeholder in the file). Never commit a real one.
   - The Streamlit-native way is `.streamlit/secrets.toml` with `GROQ_API_KEY = "gsk_..."`, read via `st.secrets["GROQ_API_KEY"]`. Add that file to `.gitignore`. See [`5_streamlitUI.md`](5_streamlitUI.md) for this approach.
   - From `3_app_search_uikeys.py` on, keys are typed into the UI, so no secrets file is needed. This is what the deployed app uses.

5. **Run**
   ```bash
   uv run streamlit run 4_stream.py
   streamlit run app.py --server.address 0.0.0.0 --server.port 8501
   ```

For how the original OpenAI tutorial code was converted to Groq, and the prompt used to do it, see [`5_streamlitUI.md`](5_streamlitUI.md).

---

## Files, in the order we built them

| File | What it adds |
|---|---|
| `1_app.py` | Official Streamlit chat tutorial, converted from OpenAI to Groq. Single full response, no streaming. |
| `2_app_search.py` | Web search (Tavily) before each answer. Results are injected as a system message. |
| `3_app_search_uikeys.py` | Groq and Tavily API keys are typed into the UI (password fields), not hardcoded. |
| `4_stream.py` | Streaming replies with `st.write_stream`. **This is the final version we deploy.** |
| `online_search.py` | Helper: `web_search(query, api_key)` wraps the Tavily client. |
| `5_streamlitUI.md` | Notes on the OpenAI → Groq conversion and the prompt used for it. |

## Step by step

### 1. `1_app.py`: OpenAI → Groq
- Source: Streamlit docs, "Build a ChatGPT-like app".
- Changes made:
  - `OpenAI` client replaced by `Groq`.
  - Model set to `openai/gpt-oss-20b`.
  - Dropped `stream=True`. The answer is read from `completion.choices[0].message.content` and shown with `st.markdown`.
- Chat history lives in `st.session_state.messages`. Streamlit reruns the script on every interaction, so history is replayed at the top of each run.
- The API key is hardcoded here. Fine for a first test, never commit it.

### 2. `2_app_search.py`: add web search
- For each user prompt, call `web_search(prompt)` and get Tavily results.
- Build a copy of the history and append a system message: `Use these web search results to answer the user: ...`.
- The system message goes only into the request. It is not saved in `st.session_state.messages`, so history stays clean.

### 3. `3_app_search_uikeys.py`: keys from the UI
- Two `st.text_input(..., type="password")` fields for the Groq and Tavily keys.
- `st.stop()` halts the script until both are filled, so the chat doesn't render without keys.
- `web_search` now takes the key as a second argument.
- Why this matters for deployment: nobody's key lives in the repo or in Streamlit secrets. Each visitor uses their own.

### 4. `4_stream.py`: streaming
- `stream=True` on the Groq call.
- Groq's chunks are not plain text, so a generator is passed to `st.write_stream`:
  ```python
  response = st.write_stream(
      chunk.choices[0].delta.content or ""
      for chunk in completion
  )
  ```
  `write_stream` returns the full text, which is then saved to history.

## Run locally

See section 0. Run `uv run streamlit run 4_stream.py` and paste both keys into the app when it loads.

## Deploy on Streamlit Community Cloud

### A. Prepare the repo
1. Dependencies: if the project was created with `uv init`, the `pyproject.toml` that `uv add streamlit groq tavily-python` updates is enough. Streamlit Cloud can install from it, so no `requirements.txt` is needed.
   - Check that `streamlit`, `groq` and `tavily-python` appear under `dependencies` in `pyproject.toml`.
   - Commit `pyproject.toml` (and `uv.lock` if present) in the repo root or next to the app.
   - Use only one dependency file. If both `requirements.txt` and `pyproject.toml` exist, Streamlit Cloud uses just one of them.
   - Without uv, use a `requirements.txt` listing the same three packages.
2. Keep `online_search.py` in the same folder as `4_stream.py`, since the app imports it.
3. Make sure no real API key is in any file. Use the placeholder in `1_app.py` and `2_app_search.py`, or leave those two out of the repo.

### B. Push to GitHub
```bash
git add 42_course_Sep/00_Day1/03_streamlit
git commit -m "Add Streamlit Groq + Tavily web agent"
git push
```
The repo must be reachable by Streamlit Cloud. Public is simplest; private works if you grant access during GitHub sign-in.

### C. Connect Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
2. Click **Create app** → **Deploy a public app from GitHub**.
3. Fill in:
   - **Repository:** your GitHub repo
   - **Branch:** `main`
   - **Main file path:** `42_course_Sep/00_Day1/03_streamlit/4_stream.py`
4. Optionally set a custom app URL, then click **Deploy**.
5. Wait for the build. Open the URL and paste your keys in the app.

Every later `git push` to that branch redeploys automatically.

## Test prompts

Use these to check that web search is working. The answer should contain recent items, not the model's training data.

```
latest AI news in short with date of publish
```

## Known issues to fix before publishing

- **`2_app_search.py` is broken as-is.** It calls `web_search(prompt)` with one argument, but `online_search.py` now requires `(query, api_key)`. Step 3 fixed this; step 2 is only valid with the older one-argument helper.
- **Search runs on every message**, even for "hi". It costs a Tavily credit and can push irrelevant results into context.
- **Keys disappear on a full page refresh.** Text inputs aren't persisted, which is expected for this design.
