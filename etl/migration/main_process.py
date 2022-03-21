from datetime import datetime
from logging import getLogger
from typing import Iterable, List

from .es_upload import UploadBatch
from .state import JsonFileStorage, State

logger = getLogger(__name__)


class UnifiedProcess:
    validation_model = None
    _local_state = {}

    def __init__(
        self, config, postgres_connection, es_settings: dict, es_index_name: str
    ):
        self.config = config
        self.conn_postgres = postgres_connection
        json_storage = JsonFileStorage(file_path=self.config.state_file_path)
        self.state = State(storage=json_storage)
        self._local_state = self.state.storage.retrieve_state()

        self.es_settings = es_settings
        self.es_index_name = es_index_name

    def get_validation_model(self):
        return getattr(self, "validation_model")

    def migrate(self):
        try:
            producer_data = self.config.producer_queries
            updated_ids = self._get_updated_item_ids(producer_data)

            for rich_data in self.enrich_data(updated_ids):
                ready_data = self.transform(rich_data)
                self._es_upload_batch(ready_data)

        except Exception:
            logger.exception("During  postgres data processing an error occurred ")

        if self._local_state:
            self.state.storage.save_state(self._local_state)

    @staticmethod
    def _get_offset(step, start=0):
        count = start
        while True:
            yield count
            count += step

    def enrich_data(self, item_ids: Iterable) -> dict:
        if not item_ids:
            return

        with self.conn_postgres.cursor() as cursor:
            query = self.config.enricher_query

            for offset in self._get_offset(self.config.limit):
                limited_query = f"{query} LIMIT {self.config.limit} OFFSET {offset}"
                cursor.execute(limited_query, (tuple(item_ids),))

                enriched_data = cursor.fetchall()
                if enriched_data:
                    yield enriched_data
                else:
                    return

    def transform(self, items: Iterable) -> Iterable:
        """
        Transformation and Validation
        """
        validation_model = self.get_validation_model()
        if not validation_model:
            return items
        return [validation_model.parse_obj(item).dict() for item in items]

    def _handle_no_date(self, query_data) -> str:
        updated_at = self.state.get_state(f"{query_data.table}_updated_at")
        latest_value = updated_at if updated_at else datetime.min.isoformat()

        sql_query_params = f"""WHERE {query_data.state_field} > ('{latest_value}')"""
        return sql_query_params

    def _get_updated_item_ids(self, producer_data: List) -> set:
        with self.conn_postgres.cursor() as cursor:
            items = set()
            for data in producer_data:
                query_tail = self._handle_no_date(data)
                query = " ".join([data.query, query_tail])

                mogrify_query = cursor.mogrify(query)
                cursor.execute(mogrify_query)
                query_data = cursor.fetchall()
                items.update(item[0] for item in query_data)

                if query_data:
                    latest_date = max(item[1] for item in query_data)
                    updated_field_name = f"{data.table}_updated_at"
                    self._local_state[updated_field_name] = str(latest_date)
            return items

    def _es_upload_batch(self, data: Iterable) -> None:
        es = UploadBatch(es_dsl=self.es_settings, index_name=self.es_index_name)
        es.es_push_batch(data=data)
