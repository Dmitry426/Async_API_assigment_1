from pydantic.validators import UUID

from .base import JsonConfig


class Genre(JsonConfig):
    id: UUID
    name: str
