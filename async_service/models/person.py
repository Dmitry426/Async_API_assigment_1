from typing import List

from pydantic.validators import UUID

from .base import JsonConfig


class Person(JsonConfig):
    id: UUID
    full_name: str
    role: List[str]
    film_works: List[UUID]
