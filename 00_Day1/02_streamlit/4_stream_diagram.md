# 4_stream.py: final app (UI keys + search + streaming)

Pick this when: deploying, or showing the finished version. This is the file used on Streamlit Cloud.

```mermaid
flowchart TD
    A([Script runs / reruns]) --> B[/Groq key + Tavily key<br/>password text inputs/]
    B --> C{Both keys<br/>filled?}
    C -- No --> C1[st.info message] --> S([st.stop])
    C -- Yes --> D[Create Groq client<br/>with typed key]
    D --> E[Init session_state:<br/>groq_model, messages]
    E --> F[Replay old messages]
    F --> G{User typed<br/>in chat_input?}
    G -- No --> Z([Wait for next interaction])
    G -- Yes --> H[Append + show user msg]
    H --> I[["web_search(prompt, tavily_key)"]]
    I --> J[Copy history + append<br/>system msg with results]
    J --> K[Groq completion<br/>stream=True]
    K --> L[st.write_stream over<br/>chunk.choices 0 .delta.content]
    L --> M[write_stream returns<br/>full text]
    M --> N[Append assistant msg<br/>to session_state]
    N --> Z
```
