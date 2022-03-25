from typing import List, Optional

from pydantic import BaseModel
from pydantic.validators import UUID

from .base import JsonConfig


class PersonGenreFilm(BaseModel):
    id: UUID
    name: str


class Film(JsonConfig):
    id: UUID
    rating: float = None
    genres: Optional[List[PersonGenreFilm]]
    title: str = None
    roles: Optional[str] = None
    description: str = None
    directors: Optional[List[PersonGenreFilm]]
    actors_names: Optional[List[str]]
    writers_names: Optional[List[str]]
    actors: Optional[List[PersonGenreFilm]]
    writers: Optional[List[PersonGenreFilm]]
