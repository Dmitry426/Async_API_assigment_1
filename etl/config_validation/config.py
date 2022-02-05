from pydantic.main import BaseModel

from .db_settings import PostgresSettings, PersonSettings


class Config(BaseModel):
    film_work_pg: PostgresSettings
    person_pg: PersonSettings
