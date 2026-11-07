# e1_pydantic_basics.py: doubts, answered short

Run: `uv run python examples/e1_pydantic_basics.py`

## 1. What does `!r` mean? (step 2)

In an f-string, `!r` means "show this value using `repr()`", the form closest to how you'd write it in code.

| Code | Output |
|---|---|
| `{movie!r}` | `Movie(id=1, title='Inception', genre='Sci-Fi')` |
| `{movie.title!r}` | `'Inception'` (quotes show it's a string) |
| `{movie.title}` | `Inception` |

Why we use it: `1` and `'1'` look the same without it. With `!r` you can tell them apart.

## 2. Why `type(movie.title).__name__`?

- `type(movie.title)` prints `<class 'str'>` , its a class object.
- Adding `.__name__` prints just `str`, its just the class name.
- It's for readable output only. For real checks, use `isinstance(x, str)`.

## 2.1 Why not use `movie.title.__name__`?
Because movie.title is a string value, not a class.
- `movie.title.__name__` , will raises error `AttributeError: 'str' object has no attribute '__name__' `
## 3. Attribute vs method vs dunder

- **Attribute:** a value on an object. No parentheses. `movie.title`, `str.__name__`.
- **Method:** an attribute that is a function. Needs `()`. `"hi".upper()`, `movie.model_dump()`.
- **Dunder:** a name with double underscores on both sides, like `__name__` or `__init__`. Python reserves them.
  - `__name__` is a dunder **attribute** (data).
  - `__init__`, `__len__`, `__repr__` are dunder **methods**. Python calls them for you, so you write `len(x)`, not `x.__len__()`.

## 4. Does `dir()` show dunders? How do I check?

`dir(obj)` lists the names on an object, including dunders. It doesn't tell you if each is a method or an attribute.

```python
"__len__" in dir("hi")                  # True
callable(getattr("hi", "__len__"))      # True, so it's a method
[n for n in dir(obj) if not n.startswith("_")]   # hide the dunders
```

Watch out: `dir(str)` does **not** list `__name__`. That attribute comes from `type` (the class of all classes), and `dir()` skips it.

To check if something exists, use `hasattr`. It is reliable.
```python
hasattr(str, "__name__")     # True
hasattr("hi", "__name__")    # False
```

## 5. What is coercion? (step 4)

Coercion means Pydantic quietly converts a value to the declared type.

```python
movie = Movie(id="5", ...)   # id is declared int
movie.id                     # 5, an int, not '5'
```

- Convertible (`"5"`) becomes `5`.
- Not convertible (`"abc"`) raises a validation error.

## 6. Isn't Pydantic meant to stop wrong types?

Yes. Its goal is that your code **always gets the right type**.

- Wrong type, but safe to convert: converted.
- Wrong type, can't convert: rejected.

Either way, `movie.id` is a real `int` once the object exists. Strict mode rejects even the convertible case:

```python
from pydantic import ConfigDict

class Movie(BaseModel):
    model_config = ConfigDict(strict=True)
    id: int
```

Now `Movie(id="5", ...)` raises an error.

## 7. What does step 5 teach? (defaults)

A default value makes a field optional. No default means required.

```python
class MovieWithDefault(BaseModel):
    id: int                    # required
    title: str                 # required
    genre: str = "Unknown"     # optional, falls back to "Unknown"
```

- Leave out `genre` and you get `"Unknown"`.
- Leave out `id` or `title` and you get a validation error.
- The default can be any value of the right type (`""`, `0`, and so on). It is not always `"Unknown"`.
- A passed value always wins over the default.
- A default doesn't allow `None`. For a field that can really be empty, write `genre: str | None = None`.

## 8. What does "model" mean in step 6?

It is not only the schema. The word covers three related things:

- **Model class:** `Movie`, the class that extends `BaseModel`. It defines the fields and types, so this part is the schema.
- **Model instance:** `movie = Movie(id=1, title="Inception", genre="Sci-Fi")`. A real object holding actual values.
- **Schema:** just the shape (names, types, required or not). `Movie.model_json_schema()` produces it. It holds no values.

Step 6 is about the **instance**, since only it has data to convert:

```python
movie.model_dump()        # {'id': 1, 'title': 'Inception', 'genre': 'Sci-Fi'}
movie.model_dump_json()   # '{"id":1,"title":"Inception","genre":"Sci-Fi"}'
```
FastAPI does this for you. When your function returns a `Movie`, it converts it to JSON for the response.
## 8.1 what is the difference between movie.model_dump() and movie.model_dump_json()?

`movie.model_dump()`
- Returns a native Python dictionary.
- You can access values using dictionary keys.
- You can modify the data like a normal dictionary.

`movie.model_dump_json()`
- Returns a JSON-formatted string.
- It is useful when sending data over HTTP APIs, writing JSON files, or storing JSON text.
- You cannot access fields directly using dictionary keys.

## 8.2 How to use Json-formatted string to filter it like dict?
- You first need to convert the JSON string into a Python dictionary using `json.loads()`
```python
import json

movie_json = movie.model_dump_json()

# Convert JSON string into Python dictionary
movie_dict = json.loads(movie_json)

# Now access fields like a dictionary
print(movie_dict["title"])
print(movie_dict["id"])
```

