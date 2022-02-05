from typing import List

import orjson
from pydantic.validators import UUID
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class Person(BaseModel):
    id: UUID
    full_name: str
    role: str
    film_ids: List[UUID]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
