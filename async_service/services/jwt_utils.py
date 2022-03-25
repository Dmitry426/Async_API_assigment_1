from abc import abstractmethod
from http.client import HTTPException
from typing import Optional

import jwt
from fastapi import HTTPException


class Auth:
    secret_key: str
    algorithm: str

    @property
    @abstractmethod
    def secret_key(self) -> str:
        pass

    @property
    @abstractmethod
    def algorithm(self) -> str:
        pass

    def decode_token(self, token: Optional[str] = None):
        try:
            payload = jwt.decode(
                token,
                key=self.secret_key,
                do_verify=True,
                do_time_check=True,
                algorithms=self.algorithm,
            )
            return payload["sub"]
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
