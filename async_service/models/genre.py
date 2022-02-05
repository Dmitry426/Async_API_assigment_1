import orjson
from pydantic.validators import UUID
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class Genre(BaseModel):
    id: UUID
    name: str

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
