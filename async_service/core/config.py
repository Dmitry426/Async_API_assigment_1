import os
from logging import config as logging_config

from dotenv import load_dotenv
from pydantic.env_settings import BaseSettings
from pydantic.fields import Field

from async_service.core.logger import LOGGING

logging_config.dictConfig(LOGGING)
load_dotenv()

logging_config.dictConfig(LOGGING)


class EsSettings(BaseSettings):
    host: str = Field("127.0.0.1", env="ELASTIC_HOST")
    port: str = Field("5432", env="ELASTIC_PORT")


class RedisSettings(BaseSettings):
    host: str = Field("127.0.0.1", env="REDIS_HOST")
    port: str = Field("6379", env="REDIS_PORT")
    db: int = Field(0, env="REDIS_DB")
    cache_ttl = Field(3600, env="API_CACHE_TTL")


class UvicornURL(BaseSettings):
    host: str = Field("127.0.0.1", env="UVICORN_HOST")
    port: str = Field("8000", env="UVICORN_PORT")


class JwtSettings(BaseSettings):
    secret_key: str = Field("super-secret-key", env="JWT_SECRET_KEY")
    algorithm: str = Field("HS256", env="ALGORITHM")


class ProjectSettings(BaseSettings):
    base_dir: str = Field(os.path.dirname(os.path.abspath(__file__)))
    project_name: str = Field("movies", env="PROJECT_NAME")
