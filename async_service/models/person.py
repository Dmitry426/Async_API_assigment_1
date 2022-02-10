from typing import List

import orjson
from pydantic import BaseModel
from pydantic.validators import UUID


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class Person(BaseModel):
    id: UUID
    full_name: str
    role: List[str]
    film_works: List[UUID]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
