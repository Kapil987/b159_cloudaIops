# e2_fastapi_basics.py: doubts, answered short

Run: `uv run uvicorn examples.e2_fastapi_basics:app --reload`
Docs: http://127.0.0.1:8000/docs

## 1. What does `genre: str = "Any"` mean? (step 4, `/search`)

```python
@app.get("/search")
def search_movies(genre: str = "Any"):
    return {"searching_for_genre": genre}
```

- `genre: str` means the parameter is a string.
- `= "Any"` is the default value, plain text. It is not a special keyword.
- A default makes the parameter optional (same rule as defaults in e1).
- `genre` is not in the path (`/search`), so FastAPI reads it from the URL after the `?`. That is a query parameter.

| Request | Result |
|---|---|
| `/search?genre=Sci-Fi` | `{"searching_for_genre": "Sci-Fi"}` |
| `/search` | `{"searching_for_genre": "Any"}` |

`"Any"` is just a label for "no filter". It could be `"All"` or `""`. It is not `typing.Any`, which is a type hint meaning "any type" and has no quotes.

## Step 2

1. `type(movie_id)` returns a Python class object, not a string.

```python
type(movie_id)  # <class 'int'>
```
2. FastAPI converts your returned Python dictionary into JSON.
3. JSON supports data types such as:
   - String
   - Integer
   - Float
   - Boolean
   - Null
   - Array
   - Object
4. A Python class object (`<class 'int'>`) is not a valid JSON data type.
5. Therefore, you convert it into a string:
   ```
   str(type(movie_id))
   ```
   Result: `"<class 'int'>"`

One important distinction: FastAPI does not automatically convert every Python object into JSON. The returned data must be JSON-serializable.
