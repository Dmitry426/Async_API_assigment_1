from typing import List, Optional

import orjson
from pydantic import BaseModel
from pydantic.validators import UUID


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class PersonFilmWork(BaseModel):
    id: UUID
    name: str


class GenreFilmWork(BaseModel):
    genre: str
    id: UUID


class Film(BaseModel):
    id: UUID
    imdb_rating: float = None
    genres: Optional[List[GenreFilmWork]]
    title: str = None
    description: str = None
    directors: Optional[List[PersonFilmWork]]
    actors_names: Optional[List[str]]
    writers_names: Optional[List[str]]
    actors: Optional[List[PersonFilmWork]]
    writers: Optional[List[PersonFilmWork]]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class Person(BaseModel):
    id: UUID
    full_name: str
    role: str
    film_ids: List[UUID]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class Genre(BaseModel):
    id: UUID
    genre: str

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
