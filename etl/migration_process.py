import logging

from psycopg2 import OperationalError, DatabaseError

from postgres_loader import Load_data
from transform_data import Data_Merger
from etl_uploader import Upload_batch
from state_operator import State_operator


class MainProcess:
    """
    Main migration process is not supposed to be initialized ,
    created in order to be inherited by specific  migration class like FilmWorkProcess
    """

    def __init__(self, config, postgres_connection):
        self.config = config
        self.loader_process = Load_data(config=self.config)
        self.conn_postgres = postgres_connection
        self.transform_data = Data_Merger()
        self.state = State_operator(self.config)
        self.logger = logging.getLogger("migrate_etl")
        self.sql_query_film_work_by_id = self.config.sql_query_film_work_by_id

    def _es_upload_butch(self, data: dict):
        es = Upload_batch(config=self.config)
        es.es_push_butch(data=data)

    def _film_work_process(self, cursor, film_work_query, state_field_name):
        for loaded in iter(
            lambda: self.loader_process.postgres_producer(
                cursor=cursor, query=film_work_query, state_field_name=state_field_name
            ),
            [],
        ):
            parsed_data = self.transform_data.handle_merge_cases(query_data=loaded)
            self._es_upload_butch(data=parsed_data)
            self.state.validate_save_timestamp(
                state_field_name=state_field_name, timestamp=loaded[-1]["updated_at"]
            )

    def _person_or_genre_process(
        self,
        cursor,
        person_or_genre_query: str,
        person_genre_fw_query: str,
        state_field_name: str,
    ):
        for loaded in iter(
            lambda: self.loader_process.postgres_producer(
                cursor=cursor,
                query=person_or_genre_query,
                state_field_name=state_field_name,
            ),
            [],
        ):
            person_ids = (res["id"] for res in loaded)
            fw_ids = self.loader_process.postgres_enricher(
                cursor=cursor, ids=person_ids, query=person_genre_fw_query
            )
            merged_film_work = self.loader_process.postgres_merger(
                cursor=cursor, ids=fw_ids, query=self.sql_query_film_work_by_id
            )

            parsed_data = self.transform_data.handle_merge_cases(
                query_data=merged_film_work
            )
            self._es_upload_butch(data=parsed_data)
            self.state.validate_save_timestamp(
                state_field_name=state_field_name, timestamp=loaded[-1]["updated_at"]
            )


class FilmWorkProcess(MainProcess):
    """Class for postgres to ETL migration aimed to migrate
    film_work table  by updated_at"""

    def __init__(self, config, postgres_connection):
        super().__init__(config, postgres_connection)

    def migrate_film_work(self, film_work_query: str, state_filed_name: str):
        try:
            with self.conn_postgres.cursor() as cursor:
                self._film_work_process(
                    cursor=cursor,
                    film_work_query=film_work_query,
                    state_field_name=state_filed_name,
                )
                self.conn_postgres.commit()
        except (OperationalError, DatabaseError) as e:
            self.logger.exception(e)


class PersonGenreProcess(MainProcess):
    """Class for postgres to ETL migration aimed to migrate
    persons or genres tables by updated_at"""

    def __iter__(self, config, postgres_connection):
        super().__init__(config, postgres_connection)

    def migrate_genre_person(
        self,
        person_or_genre_query: str,
        person_genre_fw_query: str,
        state_filed_name: str,
    ):
        try:
            with self.conn_postgres.cursor() as cursor:
                self._person_or_genre_process(
                    cursor=cursor,
                    person_or_genre_query=person_or_genre_query,
                    person_genre_fw_query=person_genre_fw_query,
                    state_field_name=state_filed_name,
                )
                self.conn_postgres.commit()
        except (OperationalError, DatabaseError) as e:
            self.logger.exception(e)
