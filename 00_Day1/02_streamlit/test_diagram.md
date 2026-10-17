# test.py: quick check of the search helper

Pick this when: you want to test Tavily alone, without Streamlit. Run with `uv run python test.py`.

Note: it calls `web_search(query)` with one argument, but the helper needs `(query, api_key)`. It raises a TypeError as-is.

```mermaid
flowchart TD
    A([python test.py]) --> B[query = latest technology news today]
    B --> C[["web_search(query)"]]
    C -->|missing api_key| X([TypeError])
    C -.->|if api_key passed| D[Print search results]
```
