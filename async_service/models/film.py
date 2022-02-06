from typing import List, Optional

import orjson
from pydantic import BaseModel
from pydantic.validators import UUID


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class PersonGenreFilm(BaseModel):
    id: UUID
    name: str


class Film(BaseModel):
    id: UUID
    imdb_rating: float = None
    genres: Optional[List[PersonGenreFilm]]
    title: str = None
    description: str = None
    directors: Optional[List[PersonGenreFilm]]
    actors_names: Optional[List[str]]
    writers_names: Optional[List[str]]
    actors: Optional[List[PersonGenreFilm]]
    writers: Optional[List[PersonGenreFilm]]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
