from pydantic import BaseModel
from pydantic.validators import UUID


class Genre(BaseModel):
    id: UUID
    name: str
