from pydantic.env_settings import BaseSettings
from pydantic.fields import Field


class ESSettings(BaseSettings):
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
