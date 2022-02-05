import abc

from etl.migration.es_upload.upload_batch import UploadBatch
from etl.migration.merge.film_work_data_merger import FilmWorkDataMerger
from etl.migration.pg_load.film_work_load_data import FilmWorkLoadData
from etl.state.state_operator import StateOperator


class MainProcess:
    """
    Main migration process is not supposed to be initialized ,
    created in order to be inherited by specific  migration class like FilmWorkProcess
    """

    def __init__(self, config, postgres_connection, es_settings, es_index_name):
        self.config = config
        self.conn_postgres = postgres_connection
        self.es_settings = es_settings

        self.loader_process = FilmWorkLoadData(config=self.config)
        self.transform_data = FilmWorkDataMerger()
        self.state = StateOperator(self.config)
        self.es_index_name = es_index_name

    @abc.abstractmethod
    def migrate(self, *args, **kwargs):
        pass

    def _es_upload_batch(self, data: dict):
        es = UploadBatch(es_dsl=self.es_settings, index_name=self.es_index_name)
        es.es_push_batch(data=data)
