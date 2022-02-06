import abc

from etl.migration.data_merge.film_work_data_merger import FilmWorkDataMerger
from etl.migration.es_upload.upload_batch import UploadBatch
from etl.migration.pg_load.film_work_load_data import FilmWorkLoadData
from etl.state.state_operator import StateOperator


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
