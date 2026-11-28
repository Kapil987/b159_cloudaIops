# v3: the same agents, as a real web app (FastAPI + HTML/CSS/JS)

v2 proved the agents work. v3 asks a different question: **how do you put them in front of real users?** Streamlit is great for a demo, but it re-runs your script on every click and gives you little control over the server. Here the agents stay exactly as they are, and we wrap them in the shape most production systems use: an API plus a browser page.

## What changes, and what doesn't

| | v2 | v3 |
|---|---|---|
| Agents (router, Postgres, RAG, merge) | `v2_rag_plus_postgres/graph.py` | **the same file, imported unchanged** |
| Server | Streamlit | FastAPI + uvicorn |
| Page | Streamlit widgets | plain HTML, CSS and JS in [static/](static/) |
| Calling the graph | `graph.invoke(...)`, wait for everything | `graph.astream(...)`, a progress event as each agent finishes |
| Login | `st.session_state` | signed cookie, checked on the server |
| Where `client_id` comes from | the session | the server-side session. **Never the request body.** |

That the graph needed no change is the point. It takes a dict and returns a dict, with no UI code inside.

## Run it

From the project root (same `.env` as v1 and v2, with v2's Postgres running and seeded):

```bash
uv sync
uv run uvicorn v3_fastapi_ui.main:app --port 8000
```

Open http://localhost:8000. The API docs are at http://localhost:8000/docs.

Optional: set `SESSION_SECRET` in `.env` (see `.env.example`). Without it, a random one is made at start-up, so everyone is logged out whenever the server restarts.

## What you see

1. **Login.** Pick Priya or Arjun (still a mock login). The server stores who you are in a signed cookie.
2. **Ask.** Click one of the three suggested questions, in order, or type your own.
3. **Watch the agents work.** The steps tick off live: Router, then Postgres facts and/or Knowledge Base, then Answer, each with its time.
4. **Check the answer.** It cites contracts as `[NOV-003 BrightMart]`. Under it, **How this answer was built** shows the route, the SQL query chosen, the facts table and the clause passages.
5. **Stop** cancels a question in progress. **Try again** appears if a step fails.

## The API

| Endpoint | What it does |
|---|---|
| `GET /api/users` | The attorneys on the mock login page |
| `POST /api/login` `{"username"}` | Starts a session (sets the cookie) |
| `POST /api/logout` | Ends it |
| `GET /api/me` | Who is logged in, and the demo date. `user` is `null` if nobody |
| `POST /api/ask` `{"question"}` | One answer, after everything finishes (`graph.ainvoke`) |
| `POST /api/ask/stream` `{"question"}` | The same, as server-sent events: one `step` event per agent, then `done` or `error` |
| `GET /api/health` | `{"status": "ok"}` |

Only `question` is accepted. There is no `client_id` field to forge. Anything extra in the JSON is dropped, and the real `client_id` is looked up from the session.

## How async is used here (and what it is not)

- The route handlers are `async def`, and the graph is called with `astream` / `ainvoke`.
- The graph's nodes are still ordinary functions, because boto3 and psycopg are not async. LangGraph runs those in worker threads, so **the server stays free to handle other users while one question waits on Bedrock**. That is the real benefit.
- Streaming is the other benefit. The browser shows progress after about a second, not a spinner for ten.
- It does **not** make a single question faster. The steps still run one after another, because "both" needs Postgres's answer before the Knowledge Base search.

## Things worth noticing in the code

- [main.py](main.py): `current_user` is a dependency. Every route that needs a login lists it, and FastAPI returns 401 before the handler runs.
- The page ([static/app.js](static/app.js)) builds everything with `textContent`, never `innerHTML`, so a model reply cannot inject HTML. The test run included a reply containing `<script>`, which showed as plain text.
- Errors (wrong KB id, Postgres down) reach the page as `RuntimeError: ...` messages, which suits a course. A real product would log the detail and show something generic.
- `https_only=False` on the cookie is for local use. Set it to `True` behind HTTPS.
- It is still a **mock login**. The cookie is signed, so it can't be edited, but anyone can pick any attorney. Real authentication is the next step.

## What was tested

Checked with fake Bedrock and Postgres standing in, running the real v2 graph behind this server: the API (login, 401s, forged cookies, ignored `client_id`, the stream, error events), and the page in headless Edge on desktop and phone sizes (login, live steps, collapsed and open trace, Stop button, error and retry, logout). **Not tested here:** a real Bedrock Knowledge Base and a real Postgres, the same gap as v2.

## Can this go on Amazon Bedrock AgentCore Runtime?

**The agent part, yes, with small changes. The web page and mock login stay outside it.**

AgentCore Runtime runs your agent as a container. Its HTTP contract, from the AWS docs ([service contract](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-service-contract.html), [HTTP contract](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-http-protocol-contract.html)):

- The container is **ARM64**, listens on **0.0.0.0:8080**.
- `POST /invocations` takes JSON (the docs example is `{"prompt": "..."}`) and returns JSON or **server-sent events**.
- `GET /ping` returns `{"status": "Healthy"}`.
- Callers authenticate with **SigV4 or OAuth 2.0**.

What that means for v3:

| Already fits | Needs changing |
|---|---|
| FastAPI, async handlers, SSE streaming | Add `/ping` and `/invocations` (a few lines around the same `astream` loop) |
| The v2 graph, unchanged | **Identity.** Browser cookies and the mock login do not exist there. `client_id` must come from the caller's verified identity, for example a claim in the OAuth token, never from the request body. Check the docs for how the verified identity reaches your code |
| `.env`-style settings | **Postgres must be reachable from AWS.** `localhost:5433` is not. Use RDS or Aurora with the runtime attached to your VPC, or a hosted database, with the password in Secrets Manager |
| | **IAM role** for the runtime: `bedrock:InvokeModel` and `bedrock:Retrieve` on your Knowledge Base |
| | **ARM64 image** and a Dockerfile (`uv sync`, then `uvicorn ... --host 0.0.0.0 --port 8080`) |

The `bedrock-agentcore` Python SDK can handle `/ping` and the entrypoint for you. See the AgentCore get-started guide before choosing between that and hand-written routes.

The usual end state has two parts: **this page and login stay on a normal web host** (S3 + CloudFront, App Runner or ECS), and a thin backend there calls the AgentCore runtime, which holds only the agents. That also solves the browser problem, since browsers can't easily sign SigV4 requests.

I have not deployed this to AgentCore. The table comes from the AWS docs above and from reading this code.

## Try it

1. Log in as Arjun and ask the same three questions. Compare the facts table with Priya's.
2. Open DevTools, Network, click `ask/stream`, and watch the events arrive. Then find where `app.js` reads them.
3. In DevTools, edit a request to add `"client_id": "greenfield_retail"` as Priya. Confirm nothing changes.
4. Stop Postgres and ask a dates question. Where does the error show up, and which step is marked failed?
5. Add a `GET /api/contracts` endpoint that lists the client's contracts straight from `db.list_contracts`, with no LLM involved. How much of `main.py` does it reuse?
