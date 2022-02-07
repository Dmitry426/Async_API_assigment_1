import abc
from datetime import datetime

from psycopg2 import DatabaseError, OperationalError

from etl.logger import logger
from etl.migration.data_merge.film_work_data_merger import FilmWorkDataMerger
from etl.migration.es_upload.upload_batch import UploadBatch
from etl.migration.pg_load.film_work_load_data import FilmWorkLoadData
from etl.state.state import State
from etl.state.state_operator import StateOperator
from etl.state.storages.json_file_storage import JsonFileStorage


class MainProcess:
    """
    Main migration process is not supposed to be initialized ,
    created in order to be inherited by specific  migration class like FilmWorkProcess
    """

    def __init__(self,
                 config,
                 postgres_connection,
                 es_settings: dict,
                 es_index_name: str
                 ):
        self.config = config
        self.conn_postgres = postgres_connection
        self.state = StateOperator(self.config)

        self.es_settings = es_settings
        self.es_index_name = es_index_name

        self.loader_process = FilmWorkLoadData(config=self.config)
        self.transform_data = FilmWorkDataMerger()

    @abc.abstractmethod
    def migrate(self, *args, **kwargs):
        pass

    def _es_upload_batch(self, data: list):
        es = UploadBatch(es_dsl=self.es_settings, index_name=self.es_index_name)
        es.es_push_batch(data=data)


class UnifiedProcess:
    validation_model = None
    _local_state = {}

    def __init__(self, config, postgres_connection, es_settings: dict, es_index_name: str):
        self.config = config
        self.conn_postgres = postgres_connection
        json_storage = JsonFileStorage(file_path=self.config.state_file_path)
        self.state = State(storage=json_storage)

        self.es_settings = es_settings
        self.es_index_name = es_index_name

    def get_validation_model(self):
        return getattr(self, 'validation_model')

    def migrate(self):
        try:
            producer_data = self.config.producer_queries
            updated_ids = self.__get_updated_item_ids(producer_data)
            rich_data = self.enrich_data(updated_ids)
            ready_data = self.transform(rich_data)
            self._es_upload_batch(ready_data)
            self.state.storage.save_state(self._local_state)

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

    def transform(self, items):
        """
        Transformation and Validation
        """
        validation_model = self.get_validation_model()
        if not validation_model:
            return items
        return [validation_model.parse_obj(item).dict() for item in items]

    def __handle_no_date(self, query_data) -> str:
        updated_at = self.state.get_state(f'{query_data.table}_updated_at')
        latest_value = updated_at if updated_at else datetime.min.isoformat()

        sql_query_params = f"""WHERE {query_data.state_field} > ('{latest_value}')"""
        return sql_query_params

    def __get_updated_item_ids(self, producer_data):
        with self.conn_postgres.cursor() as cursor:
            items = set()
            for data in producer_data:
                query_tail = self.__handle_no_date(data)
                query = ' '.join([data.query, query_tail])

                mogrify_query = cursor.mogrify(query)
                cursor.execute(mogrify_query)
                query_data = cursor.fetchall()
                items.update(item[0] for item in query_data)

                latest_date = max(item[1] for item in query_data)
                self._local_state[f'{data.table}s_updated_at'] = str(latest_date)
            return items

    def _es_upload_batch(self, data: list):
        es = UploadBatch(es_dsl=self.es_settings, index_name=self.es_index_name)
        es.es_push_batch(data=data)
