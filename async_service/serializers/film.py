from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from async_service.models.film import PersonGenreFilm
from async_service.serializers.genre import Genre


class FilmList(BaseModel):
    id: UUID
    title: str
    rating: Optional[float]
    roles: Optional[str]


class FilmDetail(FilmList):
    description: Optional[str]
    genres: Optional[List[Genre]]
    actors: Optional[List[PersonGenreFilm]]
    writers: Optional[List[PersonGenreFilm]]
    directors: Optional[List[PersonGenreFilm]]
