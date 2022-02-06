from datetime import datetime

from psycopg2 import DatabaseError, OperationalError

from etl.config_validation.indexes import Person
from etl.logger import logger
from etl.migration.main_process import MainProcess


class GenreProcess(MainProcess):
    def __init__(self,
                 config,
                 postgres_connection,
                 es_settings: dict,
                 es_index_name: str):
        super().__init__(config=config, postgres_connection=postgres_connection, es_settings=es_settings,
                         es_index_name=es_index_name)

    def migrate(self, producer_data, order_field, state_field):
        # state loaded in MainProcess
        try:
            updated_ids = self.__get_updated_person_ids(producer_data)
            rich_data = self.enrich_data(updated_ids)
            ready_data = self._transform(rich_data)
            self._es_upload_batch(ready_data)

        except (OperationalError, DatabaseError) as e:
            logger.exception(e)
        except Exception as e:
            logger.exception(e)

    def enrich_data(self, person_ids):
        with self.conn_postgres.cursor() as cursor:
            query = self.config.enricher_query.format(ids=tuple(person_ids))
            cursor.execute(cursor.mogrify(query))
            enriched_data = cursor.fetchall()
            return enriched_data

    def _transform(self, items, ValidationModel):
        return [ValidationModel.parse_obj(item).dict() for item in items]

    def __handle_no_date(self, query_data) -> str:
        self.state.validate_load_timestamp(f'{query_data.table}_updated_at')
        latest_value = self.state.updated_at if self.state.updated_at else datetime.min.isoformat()

        sql_query_params = f"""WHERE {query_data.state_field} > ('{latest_value}')"""
        return sql_query_params

    def __get_updated_person_ids(self, producer_data):
        with self.conn_postgres.cursor() as cursor:
            id_set = set()
            for data in producer_data:
                query_tail = self.__handle_no_date(data)
                query = ' '.join([data.query, query_tail])

                cursor.execute(cursor.mogrify(query))
                query_data = cursor.fetchall()
                id_set.update(item[0] for item in query_data)

                # 4 save state
                latest_date = max(item[1] for item in query_data)
            return id_set
