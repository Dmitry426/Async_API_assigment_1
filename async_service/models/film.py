from logging import RootLogger
import orjson
from typing import Optional, List
from async_service.models import genres

from pydantic.validators import UUID
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class PersonFilmWork(BaseModel):
    id: UUID
    name: str


class Film(BaseModel):
    id: UUID
    imdb_rating: float = None
    genre: List[str]
    title: str = None
    description: str = None
    director: str = None
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
