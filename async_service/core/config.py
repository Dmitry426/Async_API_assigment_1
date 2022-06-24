import os
from logging import config as logging_config

from pydantic import BaseSettings, Field

from async_service.core.logger import LOGGING

logging_config.dictConfig(LOGGING)


class EsSettings(BaseSettings):
    """Represents elastic settings"""

    class Config:
        env_prefix = "ELASTIC_"

    host: str = "127.0.0.1"
    port: str = "5432"


class RedisSettings(BaseSettings):
    """Represents redis settings"""

    class Config:
        env_prefix = "REDIS_"

    host: str = "127.0.0.1"
    port: str = "6379"
    db: int = 0
    cache_ttl = 3600


class UvicornURL(BaseSettings):
    """Represents Uvicorn settings"""

    class Config:
        env_prefix = "UVICORN_"

    host: str = "127.0.0.1"
    port: str = "8000"


class JwtSettings(BaseSettings):
    """Represents JWT settings"""

    class Config:
        env_prefix = "JWT_"

    secret_key: str = "super-secret-key"
    algorithm: str = "HS256"


class ProjectSettings(BaseSettings):
    """Represents Project settings"""

    base_dir: str = os.path.dirname(os.path.abspath(__file__))
    project_name: str = Field("movies", env="PROJECT_NAME")
