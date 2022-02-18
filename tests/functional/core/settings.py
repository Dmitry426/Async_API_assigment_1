from pydantic.env_settings import BaseSettings
from pydantic.fields import Field


class EsSettings(BaseSettings):
    host: str = Field('127.0.0.1', env="ELASTIC_HOST")
    port: str = Field('5432', env="ELASTIC_PORT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class RedisSettings(BaseSettings):
    host: str = Field('127.0.0.1', env="REDIS_HOST")
    port: str = Field('6379', env="REDIS_PORT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class UvicornURL(BaseSettings):
    host: str = Field('127.0.0.1', env="UVICORN_HOST")
    port: str = Field('8000', env="UVICORN_PORT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class BasePath(BaseSettings):
    index_path: str = Field('./testdata/index_schemas', env="INDEX_PATH")
    data_path: str = Field('./testdata', env="DATA_PATH")