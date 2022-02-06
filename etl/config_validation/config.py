from typing import Optional, List

from pydantic.main import BaseModel


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


class ProducerData(BaseModel):
    query: str
    table: str
    state_field: str


class UnifiedSettings(BaseModel):
    state_file_path: Optional[str]
    limit: Optional[int]
    order_field: str
    state_field: str

    producer_queries: List[ProducerData]
    enricher_query: str


class Config(BaseModel):
    film_work_pg: PostgresSettings
    person_pg: UnifiedSettings
    genre_pg: UnifiedSettings
