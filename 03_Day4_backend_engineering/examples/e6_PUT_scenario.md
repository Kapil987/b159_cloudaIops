Let's trace exactly what happens.

## **1. Initial watchlist after your two POST requests**

Your POST requests add two Pydantic objects:

```
watchlist = [    Movie(id=1, title="Inception", genre="Sci-Fi"),    Movie(id=2, title="Intersteller", genre="Sci-Fi")]
```

## **2. Now you execute PUT**

Your request is:

```
PUT {{baseUrl}}/movies/1
Content-Type: application/json

{
    "id": 2,
    "title": "Inception (Updated)",
    "genre": "Thriller"
}
```

FastAPI calls:

```
def update_movie(movie_id: int, updated_movie: Movie):
```

Here are the values:

- `movie_id = 1` (extracted from URL)
- `updated_movie = Movie(id=2, title="Inception (Updated)", genre="Thriller")` (validated from JSON body)

**Notice:** Your URL ID is 1, but your request body ID is 2. Both are valid independently.

## **3. What happens inside the loop?**

```
for index, movie in enumerate(watchlist):    if movie.id == movie_id:        watchlist[index] = update_movie        return updated_movie
```

Let's trace it:

**Before PUT**

`watchlist[0]` → Movie(id=1, Inception)

`watchlist[1]` → Movie(id=2, Interstellar)

**Loop execution**

- `index = 0`
- `movie.id = 1`
- `movie_id = 1`
- Condition is TRUE.

  Bug occurs here

```
watchlist[0] = update_movie
```

You assigned the function itself, not the updated Movie object.

**After PUT**

`watchlist[0]` → function `update_movie`

`watchlist[1]` → Movie(id=2, Interstellar)

Your list still has two elements. It is not empty!

## **4. Why does GET fail afterwards?**

When you call:

```
GET {{baseUrl}}/movies
```

FastAPI tries to serialize the list into JSON.

But the list contains:

- One function object.
- One Movie object.

A Python function cannot be serialized into JSON.

Therefore, FastAPI typically returns a `an empty dict and the remaining list`.

## **5. The actual fix**

Change:

```
watchlist[index] = update_movie
```

To:

```
watchlist[index] = updated_movie
```

Now your PUT replaces the first Movie object with the updated Movie object.

**One more important point:** Your PUT URL identifies movie ID 1, but your body contains ID 2. Your current code updates movie 1 with an object whose ID is 2.

For a cleaner implementation, use:

```
@app.put("/movies/{movie_id}")def update_movie(movie_id: int, updated_movie: Movie):    for index, movie in enumerate(watchlist):        if movie.id == movie_id:            updated_movie.id = movie_id            watchlist[index] = updated_movie            return updated_movie    return {"error": "Movie not found"}
```

This ensures the URL ID remains the movie's ID.

**Key takeaway:** `update_movie` is a function name. `updated_movie` is the Pydantic object received in the request body. Python allows you to store functions inside lists, so it doesn't automatically catch this logical mistake.