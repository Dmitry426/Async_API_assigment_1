from psycopg2 import OperationalError, DatabaseError

from .main_process import MainProcess

from etl.logger import logger


class PersonGenreProcess(MainProcess):
    """Class for postgres to ETL migration aimed to migrate
    persons or genres tables by updated_at"""

    def migrate(
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
        except (OperationalError, DatabaseError) as e:
            logger.exception(e)

    def _person_or_genre_process(
            self,
            cursor,
            person_or_genre_query: str,
            person_genre_fw_query: str,
            state_field_name: str,
    ):
        def pg_producer():
            return self.loader_process.postgres_producer(
                cursor=cursor,
                query=person_or_genre_query,
                state_field_name=state_field_name,
            )

        for loaded in iter(pg_producer, []):
            person_ids = (res["id"] for res in loaded)
            fw_ids = self.loader_process.postgres_enricher(
                cursor=cursor, ids=person_ids, query=person_genre_fw_query
            )
            merged_film_work = self.loader_process.postgres_merger(
                cursor=cursor, ids=fw_ids, query=self.config.sql_query_film_work_by_id
            )

            parsed_data = self.transform_data.handle_merge_cases(
                query_result=merged_film_work
            )
            self._es_upload_batch(data=parsed_data)
            self.state.validate_save_timestamp(
                state_field_name=state_field_name, timestamp=loaded[-1]["updated_at"]
            )
