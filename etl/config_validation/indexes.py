from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel
from pydantic.class_validators import validator


class UIIDModel(BaseModel):
    id: UUID


class PersonFilmWork(UIIDModel):
    name: str


class GenreFilmWork(UIIDModel):
    name: str


class FilmWork(UIIDModel):
    rating: float
    genres: Optional[List[GenreFilmWork]]
    roles: Optional[List[str]] = None
    title: str
    description: str
    directors: Optional[List[PersonFilmWork]]
    actors_names: Optional[List[str]]
    writers_names: Optional[List[str]]
    actors: Optional[List[PersonFilmWork]]
    writers: Optional[List[PersonFilmWork]]

    @validator("description", "title")
    def handle_empty_str(cls, variable: str) -> Optional[str]:
        return variable if variable else None

    @validator("rating")
    def handle_empty_float(cls, variable: float) -> Optional[float]:
        return variable if variable else None


class Person(UIIDModel):
    full_name: str
    role: List[str]
    film_works: List[UUID]


class Genre(UIIDModel):
    name: str
