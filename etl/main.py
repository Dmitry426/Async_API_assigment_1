from time import sleep

import backoff
import psycopg2
import schedule
from dotenv import load_dotenv
from psycopg2 import OperationalError
from psycopg2.extras import DictCursor

from etl.config_validation.db_settings import DSNSettings, ESSettings
from etl.migration.person_process import PersonProcess
from logger import logger
from migration.film_work_process import FilmWorkProcess
from migration.person_genre_person import PersonGenreProcess
from config_validation.config import Config

config = Config.parse_file("config.json")
fw_config = config.film_work_pg
sql_query_film_work = fw_config.sql_query_film_work_by_updated_at
sql_query_persons = fw_config.sql_query_persons
sql_query_person_film_work = fw_config.sql_query_person_film_work
sql_query_genres = fw_config.sql_query_genres
sql_query_genre_film_work = fw_config.sql_query_genre_film_work
film_work_state_field = fw_config.film_work_state_field
genres_state_field = fw_config.genres_state_field
persons_state_field = fw_config.persons_state_field

load_dotenv()
dsl = DSNSettings().dict()
es_settings = ESSettings().dict()


@backoff.on_exception(backoff.expo, OperationalError, max_time=60)
def migrate_to_etl():
    logger.debug('migrate_to_etl()')
    with psycopg2.connect(**dsl, cursor_factory=DictCursor) as connection:
        person_to_es = PersonProcess(
            config=fw_config,
            postgres_connection=connection,
            es_settings=es_settings,
            es_index_name='person'
        )

        person_to_es.migrate(
            config.person_pg.producer_queries,
            config.person_pg.order_field,
            config.person_pg.state_field
        )

        film_work_to_es = FilmWorkProcess(
            config=fw_config,
            postgres_connection=connection,
            es_settings=es_settings,
            es_index_name='movies'
        )

        film_work_to_es.migrate(
            film_work_query=sql_query_film_work,
            state_filed_name=film_work_state_field
        )

        genres_persons_to_es = PersonGenreProcess(
            config=fw_config,
            postgres_connection=connection,
            es_settings=es_settings,
            es_index_name='movies'
        )

        genres_persons_to_es.migrate(
            person_or_genre_query=sql_query_genres,
            person_genre_fw_query=sql_query_genre_film_work,
            state_filed_name=genres_state_field,
        )

        genres_persons_to_es.migrate(
            person_or_genre_query=sql_query_persons,
            person_genre_fw_query=sql_query_person_film_work,
            state_filed_name=persons_state_field
        )


if __name__ == "__main__":
    try:
        schedule.every(1).minutes.do(migrate_to_etl)
        while True:
            schedule.run_pending()
            sleep(1)
    except psycopg2.OperationalError as e:
        logger.exception(e)
