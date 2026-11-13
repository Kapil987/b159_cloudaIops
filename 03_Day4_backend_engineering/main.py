from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
# app = FastAPI()
class Movie(BaseModel):
    id: int
    title: str
    genre: str

watchlist: list[Movie] = []


# abc.com --> welcome to our page
@app.get("/")
def read_root():
    return {"message": "welcome to your movie watchlist"}

@app.get("/movies")
def get_movies():
    return watchlist

@app.post("/movies")
def add_movie(movie: Movie):
    watchlist.append(movie)
    return movie

@app.put("/movies/{movie_id}")
def update_movie(movie_id: int, updated_movie: Movie):
    for index, movie in enumerate(watchlist):
        if movie.id == movie_id:
            watchlist[index] = update_movie
            return update_movie
        return {"error": "Movie not found"}

@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int):
    for index, movie in enumerate(watchlist):
        if movie.id == movie_id:
            deleted = watchlist.pop(index)
            return deleted
        return {"error": "Movie not found"}
