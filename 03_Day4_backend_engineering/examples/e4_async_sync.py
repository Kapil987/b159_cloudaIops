import time
from fastapi import FastAPI
import asyncio

app = FastAPI()

"""
Runs in main thread, No awaitable operation, cannot be paused
sequentail order
Request 1
    Hello
    Bye

Request 2
    Hello
    bye
"""
@app.get("/1")
async def endpoint1(): # Processed Sequentially
    print("hello")
    time.sleep(5)  # Blocking I/O Opertion, cannot be awaited
    # function execution cannot be paused, the event loop is blocked while waiting for the result
    print("bye")

"""
Runs in main thread, 
- Has awaitable operation, 
- can be paused
- Processed Concurrently
Request 1
    Hello
Request 2
    Hello

Request 1
    bye
Request 2
    bye

"""
@app.get("/2")
async def endpoint2(): # Processed Concurrently
    print("hello")
    await asyncio.sleep(5) # Non blocking IO operations, it can be awaited
    # function execution will pause, during this pause the event loop can handle other tasks
    print("bye")

"""
Runs in seperate threads, so parallel execution
- Processed Concurrently
Request 1
    Hello
Request 2
    Hello
Request 1
    bye
Request 2
    bye

"""
@app.get("/3")
def endpoint3(): # Processed parallely
    print("hello")
    time.sleep(5)
    print("bye")

# Uvicorn --> main thread
# Coroutines runs in Event Loop in main thread

"""
Best Practices
1. Use async def for endpoint with non-blocking I/O operations
2. Dont't use async def for endpoint with blocking I/O operations
3. Use Normal fucntion for endpoint with blocking I/O operations
"""