from typing import  List

from pydantic import BaseModel


class TokenData(BaseModel):
    roles: List[str] = None


class Token(BaseModel):
    access_token: str
