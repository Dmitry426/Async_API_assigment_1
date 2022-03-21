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


class TestSettings(BaseSettings):
    es_settings: EsSettings = EsSettings()
    redis_settings: RedisSettings = RedisSettings()
    url_settings: UvicornURL = UvicornURL()
    index_path: str = Field("./testdata/index_schemas")
    data_path: str = Field("./testdata/")
    api_path: str = Field("/api/v1")
    es_indexes: List[str] = List["genres", "movies", "persons"]
