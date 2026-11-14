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


### can fastapi create multiple thread for non async function or tasks can i control how many threads it will make is there a default value ?

Yes. **FastAPI automatically runs synchronous (**`def`**) endpoints in a worker thread pool.** You can also control the maximum concurrency.

The default limit is **40 concurrent worker threads per Uvicorn worker process** when using the standard FastAPI/Starlette thread-pool mechanism.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://starlette.dev\&sz=32)

Starlette+1



## **1. How FastAPI handles requests**

Consider these two endpoints:

```
import timefrom fastapi import FastAPI
app = FastAPI()
@app.get("/sync")
def sync_endpoint():    
time.sleep(5)    
return {"message": "Done"}
@app.get("/async")
async def async_endpoint():    
time.sleep(5)    
return {"message": "Done"}
```

There is an important difference:

**Endpoint 1: Normal&#x20;**`def`

Worker thread pool

FastAPI event loop

**Thread 1**

Request 1

**Thread 2**

Request 2

**Thread 3**

Request 3

Multiple synchronous requests can execute concurrently.

**Endpoint 2:&#x20;**`async def`**&#x20;with blocking code**

Blocks event loop

Event loop

`time.sleep(5)`

Other tasks on this loop are blocked

Important: The second example is deliberately incorrect async usage. Use `await asyncio.sleep(5)` or an asynchronous I/O library instead.

## **2. What is the default thread limit?**

FastAPI uses Starlette, which uses AnyIO's thread mechanism.

Default:

```
40 concurrent worker threads
```

This is a concurrency limit, not 40 threads permanently running from application startup. Threads are created when needed and reused.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://starlette.dev\&sz=32)

Starlette+1



For example:

| Concurrent sync requests | Behaviour                           |
| ------------------------ | ----------------------------------- |
| 5                        | 5 can execute concurrently          |
| 20                       | 20 can execute concurrently         |
| 40                       | Up to 40 can execute concurrently   |
| 50                       | 40 execute; remaining requests wait |

## **3. How to increase or decrease the limit**

You can configure it using AnyIO.

```
import anyio.to_thread 
from contextlib import asynccontextmanager 
from fastapi import FastAPI
@asynccontextmanagerasync 
def lifespan(app: FastAPI):    
    limiter = anyio.to_thread.current_default_thread_limiter()    
    limiter.total_tokens = 60    
    print("Thread limit:", limiter.total_tokens)    
    yield
    app = FastAPI(lifespan=lifespan)
```

Now the default thread capacity is 60 instead of 40.

You can also reduce it to 10 if you want to limit concurrent synchronous operations.

## **4. What if you have async endpoints calling synchronous functions?**

Suppose you have an async endpoint but need to call a synchronous third-party library.

Use `run_in_threadpool()`:

```
from starlette.concurrency import run_in_threadpoolimport timedef blocking_function():    time.sleep(5)    return "Completed"@app.get("/test")async def test():    result = await run_in_threadpool(blocking_function)    return {"result": result}
```

This moves the blocking function into the same AnyIO worker-thread mechanism.

## **5. Important distinction: Threads vs Uvicorn workers**

You can also start multiple Uvicorn worker processes:

```
uv run uvicorn main:app --workers 4
```

These are separate processes, not threads.

For example:

| Configuration          | Maximum sync thread capacity |
| ---------------------- | ---------------------------- |
| 1 Uvicorn worker × 40  | 40                           |
| 2 Uvicorn workers × 40 | 80                           |
| 4 Uvicorn workers × 40 | 160                          |

These are theoretical aggregate limits, assuming the default limiter in each process.

## **6. What should you use?**

| Workload                                | Recommended approach                   |
| --------------------------------------- | -------------------------------------- |
| Synchronous database library            | `def` endpoint                         |
| Async database library                  | `async def`                            |
| Synchronous HTTP client (`requests`)    | `def` or `run_in_threadpool`           |
| Async HTTP client (`httpx.AsyncClient`) | `async def`                            |
| CPU-intensive Python computation        | Process pool                           |
| Long-running background work            | Dedicated task queue where appropriate |

**My recommendation:** Don't increase the thread limit blindly. More threads consume memory and can overload databases or external APIs.

For your ServiceNow integration, if you use synchronous `requests`, a normal `def` endpoint is perfectly reasonable. If you use `httpx.AsyncClient`, use `async def`.

Further reading: [Starlette Thread Pool documentation](https://starlette.dev/threadpool/).
