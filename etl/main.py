import logging
import time

import backoff
import psycopg2
import schedule
from dotenv import load_dotenv
from psycopg2 import OperationalError
from psycopg2.extras import DictCursor

from migration_process import FilmWorkProcess, PersonGenreProcess
from validation_classes import Config, DSNSettings

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


def load_loger():
    logging.basicConfig(
        filename="es.log", filemode="w", format="%(name)s - %(levelname)s - %(message)s"
    )


@backoff.on_exception(backoff.expo, OperationalError, max_time=60)
def migrate_to_etl():
    with psycopg2.connect(**dsl, cursor_factory=DictCursor) as connection:
        film_work_to_es = FilmWorkProcess(
            config=fw_config, postgres_connection=connection
        )

        film_work_to_es.migrate_film_work(
            film_work_query=sql_query_film_work, state_filed_name=film_work_state_field
        )

        genres_persons_to_es = PersonGenreProcess(
            config=fw_config, postgres_connection=connection
        )
        genres_persons_to_es.migrate_genre_person(
            person_or_genre_query=sql_query_genres,
            person_genre_fw_query=sql_query_genre_film_work,
            state_filed_name=genres_state_field,
        )
        genres_persons_to_es.migrate_genre_person(
            person_or_genre_query=sql_query_persons,
            person_genre_fw_query=sql_query_person_film_work,
            state_filed_name=persons_state_field,
        )


if __name__ == "__main__":
    load_loger()
    try:
        schedule.every(1).minutes.do(migrate_to_etl)
        while True:
            schedule.run_pending()
            time.sleep(1)
    except psycopg2.OperationalError as e:
        logging.error(e)
