from typing import List, Optional

from pydantic import BaseModel


class TokenData(BaseModel):
    roles: Optional[List[str]]


class Token(BaseModel):
    access_token: str
