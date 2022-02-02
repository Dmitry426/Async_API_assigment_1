from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel, validator
from pydantic.validators import UUID
from pydantic import BaseSettings, Field


class DSNSettings(BaseSettings):
    host: str = Field(..., env="POSTGRES_HOST")
    port: str = Field(..., env="POSTGRES_PORT")
    dbname: str = Field(..., env="POSTGRES_DB")
    password: str = Field(..., env="POSTGRES_PASSWORD")
    user: str = Field(..., env="POSTGRES_USER")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class PostgresSettings(BaseModel):
    limit: Optional[int]
    film_work_state_field: str
    genres_state_field: str
    persons_state_field: str
    state_file_path: Optional[str]
    sql_query_film_work_by_id: str
    sql_query_persons: str
    sql_query_genres: str
    sql_query_person_film_work: str
    sql_query_genre_film_work: str
    sql_query_film_work_by_updated_at: str
    elastic_port: str


class Config(BaseModel):
    film_work_pg: PostgresSettings


class Person(BaseModel):
    id: UUID
    name: str


class Datetime_serialization(BaseModel):
    persons_updated_at: Optional[datetime] = None
    genres_updated_at: Optional[datetime] = None
    film_work_updated_at: Optional[datetime] = None


class FilmWork(BaseModel):
    id: UUID
    imdb_rating: float = None
    genre: List[str]
    title: str = None
    description: str = None
    director: str = None
    actors_names: Optional[List[str]]
    writers_names: Optional[List[str]]
    actors: Optional[List[Person]]
    writers: Optional[List[Person]]

    @validator("director", "description", "title")
    def handle_empty_str(cls, variable: str) -> str:
        if not variable:
            return None
        return variable
