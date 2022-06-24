import logging
from abc import abstractmethod
from typing import List

import jwt
from fastapi import HTTPException

logger = logging.getLogger("film_api")


class Auth:
    @property
    @abstractmethod
    def secret_key(self) -> str:
        pass

    @property
    @abstractmethod
    def algorithm(self) -> List[str]:
        pass

    def decode_token(self, token: str):
        try:
            payload = jwt.decode(
                jwt=token,
                key=self.secret_key,
                do_verify=True,
                do_time_check=True,
                algorithms=self.algorithm,
            )
            return payload["sub"]
        except jwt.ExpiredSignatureError as exc:
            logger.error(exc, exc_info=True)
            raise HTTPException(status_code=401, detail=exc) from exc
        except jwt.InvalidTokenError as exc:
            logger.error(exc, exc_info=True)
            raise HTTPException(status_code=401, detail=exc) from exc
