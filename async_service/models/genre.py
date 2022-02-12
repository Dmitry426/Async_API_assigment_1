from pydantic.validators import UUID

from .film import JsonConfig


class Genre(JsonConfig):
    id: UUID
    name: str
