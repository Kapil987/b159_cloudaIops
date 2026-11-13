Use async def if:

Calling LLM APIs
Calling databases
Calling vector stores
Making HTTP requests

Use def if:

Running heavy CPU-bound inference locally
Doing image/video processing
Running blocking legacy libraries

A good rule is:

If the library supports await, use async def. Otherwise use def. FastAPI will handle both correctly.

uvicorn <python_file_without_py>:<FastAPI_instance>