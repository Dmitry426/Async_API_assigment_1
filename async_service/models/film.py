from typing import List, Optional

from pydantic import BaseModel
from pydantic.validators import UUID

from .base import JsonConfig


class PersonGenreFilm(BaseModel):
    id: UUID
    name: str


class Film(JsonConfig):
    id: UUID
    rating: Optional[float]
    genres: Optional[List[PersonGenreFilm]]
    title: Optional[str]
    roles: Optional[str]
    description: Optional[str]
    directors: Optional[List[PersonGenreFilm]]
    actors_names: Optional[List[str]]
    writers_names: Optional[List[str]]
    actors: Optional[List[PersonGenreFilm]]
    writers: Optional[List[PersonGenreFilm]]
