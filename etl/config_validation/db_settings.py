from pydantic.env_settings import BaseSettings
from pydantic.fields import Field


class DSNSettings(BaseSettings):
    host: str = Field(..., env="POSTGRES_HOST")
    port: str = Field(..., env="POSTGRES_PORT")
    dbname: str = Field(..., env="POSTGRES_DB")
    password: str = Field(..., env="POSTGRES_PASSWORD")
    user: str = Field(..., env="POSTGRES_USER")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class ESSettings(BaseSettings):
    host: str = Field(..., env="ELASTIC_HOST")
    port: str = Field(..., env="ELASTIC_PORT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
