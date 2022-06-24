from typing import List, Optional

from pydantic import BaseModel


class ProducerData(BaseModel):
    query: str
    table: str
    state_field: str


class PostgresSettings(BaseModel):
    state_file_path: Optional[str]
    limit: Optional[int]
    order_field: str
    state_field: str

    producer_queries: List[ProducerData]
    enricher_query: str


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
