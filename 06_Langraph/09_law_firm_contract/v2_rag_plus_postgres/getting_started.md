# v2: getting started

The steps to run v2 for the first time. For what v2 does and why, see the [v2 README](README.md).

## 0. Check v1 first

v2 uses the same Knowledge Base, so v1 must already be working. `KB_ID`, `KB_TYPE`, `AWS_REGION` and `BEDROCK_MODEL_ID` in `.env` apply to both. If v1 answers a CloudServe question, you are ready.

## 1. Get a Postgres

Pick one.

**Option A: Docker** (from the project root)

```bash
docker compose -f v2_rag_plus_postgres/docker-compose.yml up -d
```

The default `POSTGRES_DSN` in `.env.example` already matches this.

**Option B: free hosted Postgres** (Neon, Supabase and similar)

Copy the connection string it gives you into `.env`:

```
POSTGRES_DSN=postgresql://user:pass@host/dbname?sslmode=require
```

If the first question times out, the database may be waking from idle. Raise `connect_timeout=5` in [db.py](db.py) to about 15.

## 2. Create the table and load the data

```bash
uv run python v2_rag_plus_postgres/seed.py
```

Expected output: `Loaded 8 contracts.` You can run it again safely. If it fails with a connection error, Postgres is not reachable yet.

## 3. Start the app

```bash
uv run streamlit run v2_rag_plus_postgres/app.py
```

The page header should say "Today's date in this demo: 01 Dec 2026".

## 4. Test in this order

Log in as **Priya**. Under each answer, open **How this answer was built** and check the route.

| Ask | Route | Expected answer |
|---|---|---|
| Which contracts expire in the next 90 days? | `metadata` | NOV-004 (20 Jan 2027), NOV-006 (5 Feb), NOV-003 (15 Feb), NOV-002 (28 Feb) |
| What does the liability clause say in the CloudServe contract? | `rag` | Capped at 12 months of fees |
| Which contracts auto-renew within 90 days and have unlimited liability? | `both` | NOV-003 and NOV-006. Not NOV-002 (capped) and not NOV-004 (does not renew) |

Then log in as **Arjun** and ask the first question again. You should see only GRN-002, whose notice deadline (11 Nov 2026) has already passed.

## If something fails

| Problem | Likely cause |
|---|---|
| `connection timeout expired` | Postgres is not running, or `POSTGRES_DSN` is wrong |
| `relation "contracts" does not exist` | `seed.py` was not run |
| Wrong route in the trace panel | `amazon.nova-micro-v1:0` is a small model. Try a stronger `BEDROCK_MODEL_ID` |
| The `both` question gives a partial answer | Check the trace panel: which contracts did Postgres return, and which passages came back? |

The SQL in [db.py](db.py) has not been run against a real Postgres yet, so a query error on the first run is possible. Read the full error message in the app.
