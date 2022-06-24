from typing import List
from uuid import UUID

from .base import UuidModel


class PersonGenreFilm(UuidModel):
    name: str


class Person(UuidModel):
    full_name: str
    role: List[str]
    film_works: List[UUID]
