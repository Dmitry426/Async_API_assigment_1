from typing import Optional, List

from pydantic.env_settings import BaseSettings
from pydantic.fields import Field
from pydantic.main import BaseModel


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
    connection_url: str = Field(..., env="ES_CONNECTION")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class PostgresSettings(BaseModel):
    limit: Optional[int]
    film_work_state_field: str
    genres_state_field: str
    persons_state_field: str
    state_file_path: Optional[str]

    sql_query_film_work_by_updated_at: str

    sql_query_film_work_by_id: str
    sql_query_persons: str
    sql_query_genres: str
    sql_query_person_film_work: str
    sql_query_genre_film_work: str


class PersonSettings(BaseModel):
    state_file_path: Optional[str]
    limit: Optional[int]
    order_field: str
    state_field: str

    producer_queries: List[str]
