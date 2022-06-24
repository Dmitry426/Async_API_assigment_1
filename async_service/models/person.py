from typing import List
from uuid import UUID

from .base import BaseOrjson


class Person(BaseOrjson):
    full_name: str
    role: List[str]
    film_works: List[UUID]
