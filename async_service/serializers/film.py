from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel

from async_service.models.film import PersonGenreFilm
from async_service.serializers.genre import Genre


class FilmList(BaseModel):
    id: UUID
    title: str
    rating: float = None
    roles: Optional[str] = None


class FilmDetail(FilmList):
    description: Optional[str]
    genres: Optional[List[Genre]]
    actors: Optional[List[PersonGenreFilm]]
    writers: Optional[List[PersonGenreFilm]]
    directors: Optional[List[PersonGenreFilm]]
