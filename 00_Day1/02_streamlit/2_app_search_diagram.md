# 2_app_search.py: chat + Tavily web search

Pick this when: you want to show how search results are fed to the model. Key is hardcoded.

Note: this file calls `web_search(prompt)` with one argument, but `online_search.py` now needs `(query, api_key)`. It fails as-is (see README, Known issues).

```mermaid
flowchart TD
    A([Script runs / reruns]) --> B[Create Groq client<br/>hardcoded key]
    B --> C[Init session_state:<br/>groq_model, messages]
    C --> D[Replay old messages]
    D --> E{User typed<br/>in chat_input?}
    E -- No --> Z([Wait for next interaction])
    E -- Yes --> F[Append + show user msg]
    F --> G[["web_search(prompt)<br/>online_search.py → Tavily"]]
    G --> H[Copy history into local<br/>messages list]
    H --> I[Append system msg with<br/>search results<br/>request only, not saved]
    I --> J[Groq completion<br/>no stream]
    J --> K[st.markdown response]
    K --> L[Append assistant msg<br/>to session_state]
    L --> Z
```
