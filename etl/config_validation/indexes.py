from typing import Optional, List

from pydantic.class_validators import validator
from pydantic.main import BaseModel
from pydantic.validators import UUID


class PersonFilmWork(BaseModel):
    id: UUID
    name: str


class GenreFilmWork(BaseModel):
    id: UUID
    genre: str


class FilmWork(BaseModel):
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

    @validator("description", "title")
    def handle_empty_str(cls, variable: str) -> str:
        return variable if variable else None


class Person(BaseModel):
    id: UUID
    full_name: str
    role: List[str]
    film_works: List[UUID]


class Genre(BaseModel):
    id: UUID
    name: str
