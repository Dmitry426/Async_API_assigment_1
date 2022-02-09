from time import sleep

import backoff
import psycopg2
import schedule
from dotenv import load_dotenv
from psycopg2 import OperationalError
from psycopg2.extras import DictCursor

from config_validation.config import Config
from etl.config_validation.db_settings import DSNSettings, ESSettings
from etl.migration.film_work_process import FilmWorkProcess
from etl.migration.genre_process import GenreProcess
from etl.migration.person_process import PersonProcess
from logger import logger

config = Config.parse_file("config.json")

load_dotenv()
dsl = DSNSettings().dict()
es_settings = ESSettings().dict()


@backoff.on_exception(backoff.expo, OperationalError, max_time=60)
def migrate_to_etl():
    with psycopg2.connect(**dsl, cursor_factory=DictCursor) as connection:
        film_work_to_es = FilmWorkProcess(
            config=config.film_work_pg,
            postgres_connection=connection,
            es_settings=es_settings,
            es_index_name='movies'
        )
        film_work_to_es.migrate()

        person_to_es = PersonProcess(
            config=config.person_pg,
            postgres_connection=connection,
            es_settings=es_settings,
            es_index_name='persons'
        )
        person_to_es.migrate()

        genre_to_es = GenreProcess(
            config=config.genre_pg,
            postgres_connection=connection,
            es_settings=es_settings,
            es_index_name='genres'
        )
        genre_to_es.migrate()


if __name__ == "__main__":
    try:
        schedule.every(1).minutes.do(migrate_to_etl)
        while True:
            schedule.run_pending()
            sleep(1)
    except psycopg2.OperationalError as e:
        logger.exception(e)
