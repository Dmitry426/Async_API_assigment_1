from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from .base import BaseOrjson


class PersonGenreFilm(BaseModel):
    id: UUID
    name: str


class Film(BaseOrjson):
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
