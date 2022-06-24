from uuid import UUID

import orjson
from pydantic import BaseModel


def orjson_dumps(cls, *, default):
    return orjson.dumps(cls, default=default).decode()


class BaseOrjson(BaseModel):
    id: UUID

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
