# Example 1: Async vs Sync FastAPI Endpoints

This README explains `e4_async_sync.py`.

The file compares three FastAPI endpoint patterns:

- `/1`: `async def` endpoint with blocking `time.sleep(5)`
- `/2`: `async def` endpoint with non-blocking `await asyncio.sleep(5)`
- `/3`: normal `def` endpoint with blocking `time.sleep(5)`

## Run The Example

From the `29_fastAPI` folder:

```powershell
uv run uvicorn examples.e4_async_sync:app --reload
```

Or from the `29_fastAPI/examples` folder:

```powershell
uv run uvicorn e4_async_sync:app --reload
```

The server runs at:

```text
http://127.0.0.1:8000
```

## Test From CLI

Open two terminals and call the same endpoint quickly in both terminals.

Terminal 1:

```powershell
curl http://127.0.0.1:8000/1
```

Terminal 2:

```powershell
curl http://127.0.0.1:8000/1
```

Repeat the same test for `/2` and `/3`:

```powershell
curl http://127.0.0.1:8000/2
curl http://127.0.0.1:8000/3
```

The endpoints do not return custom data, so the HTTP response body is `null`.
The important output is printed in the server terminal:

```text
hello
bye
```

## CLI Diagram

```text
Client terminals
    |
    |  curl /1 twice
    v
FastAPI endpoint: async def + time.sleep(5)
    |
    |  time.sleep blocks the event loop
    v
Request 1: hello ---- wait 5s ---- bye
Request 2:                         hello ---- wait 5s ---- bye

Result: sequential behavior
```

```text
Client terminals
    |
    |  curl /2 twice
    v
FastAPI endpoint: async def + await asyncio.sleep(5)
    |
    |  await pauses this coroutine and frees the event loop
    v
Request 1: hello ---- async wait 5s ---- bye
Request 2: hello ---- async wait 5s ---- bye

Result: concurrent behavior on the event loop
```

```text
Client terminals
    |
    |  curl /3 twice
    v
FastAPI endpoint: def + time.sleep(5)
    |
    |  FastAPI runs sync endpoints in worker threads
    v
Request 1: hello ---- thread sleep 5s ---- bye
Request 2: hello ---- thread sleep 5s ---- bye

Result: concurrent behavior using threads
```

## What Each Endpoint Shows

### `/1`: Bad Async Pattern

```python
@app.get("/1")
async def endpoint1():
    print("hello")
    time.sleep(5)
    print("bye")
```

This endpoint is declared with `async def`, but it uses `time.sleep(5)`.
`time.sleep` is blocking and cannot be awaited, so it blocks the main event loop.
While it is sleeping, other async work cannot run.

Use this only as a learning example.

### `/2`: Correct Async Pattern

```python
@app.get("/2")
async def endpoint2():
    print("hello")
    await asyncio.sleep(5)
    print("bye")
```

This endpoint uses an awaitable operation.
While `asyncio.sleep(5)` is waiting, the coroutine pauses and the event loop can handle other requests.

Use `async def` when the operation supports `await`, such as async database calls, async HTTP clients, or async LLM API calls.

### `/3`: Correct Sync Pattern For Blocking Work

```python
@app.get("/3")
def endpoint3():
    print("hello")
    time.sleep(5)
    print("bye")
```

This endpoint is a normal function.
FastAPI runs normal `def` endpoints in a thread pool, so blocking work does not block the main event loop.

Use `def` when the operation is blocking and does not support `await`.

## Rule Of Thumb

```text
Does the operation support await?

Yes -> use async def
No  -> use def
```

Examples:

- Use `async def` for async database clients, async HTTP clients, and async API calls.
- Use `def` for blocking libraries, `time.sleep`, CPU-heavy local work, and legacy sync code.
