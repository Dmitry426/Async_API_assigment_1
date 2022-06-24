from uuid import UUID

from pydantic import BaseModel


class UuidModel(BaseModel):
    id: UUID
