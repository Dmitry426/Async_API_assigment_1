from typing import List

from pydantic import BaseModel
from pydantic.validators import UUID


class PersonGenreFilm(BaseModel):
    id: UUID
    name: str
    

class Person(BaseModel):
    id: UUID
    full_name: str
    role: List[str]
    film_works: List[UUID]
