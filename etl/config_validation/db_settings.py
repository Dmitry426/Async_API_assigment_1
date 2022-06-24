from pydantic.env_settings import BaseSettings


class DSNSettings(BaseSettings):
    class Config:
        env_prefix = "POSTGRES_"

    host: str
    port: str
    dbname: str
    password: str
    user: str


class ESSettings(BaseSettings):

    class Config:
        env_prefix = "ELASTIC_"

    host: str
    port: str


