from typing import List

from pydantic.env_settings import BaseSettings
from pydantic.fields import Field


class EsSettings(BaseSettings):
    host: str = Field("127.0.0.1", env="ELASTIC_HOST")
    port: str = Field("5432", env="ELASTIC_PORT")


class RedisSettings(BaseSettings):
    host: str = Field("127.0.0.1", env="REDIS_HOST")
    port: str = Field("6379", env="REDIS_PORT")
    db: int = Field(0, env="REDIS_DB")


class UvicornURL(BaseSettings):
    host: str = Field("127.0.0.1", env="UVICORN_HOST")
    port: str = Field("8000", env="UVICORN_PORT")


class JwtSettings(BaseSettings):
    secret_key: str = Field("super-secret-key", env="JWT_SECRET_KEY")
    algorithm: str = Field("HS256", env="ALGORITHM")


class TestSettings(BaseSettings):
    jwt_settings: JwtSettings = JwtSettings()
    es_settings: EsSettings = EsSettings()
    redis_settings: RedisSettings = RedisSettings()
    url_settings: UvicornURL = UvicornURL()
    index_path: str = Field("testdata/index_schemas")
    data_path: str = Field("testdata/")
    api_path: str = Field("/api/v1")
    es_indexes: List[str] = ["genres", "movies", "persons"]
    ping_timeout: int = Field(30, env="PING_BACKOFF_TIMEOUT")
