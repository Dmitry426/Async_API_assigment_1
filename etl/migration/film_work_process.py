from .main_process import UnifiedProcess

# class FilmWorkProcess(MainProcess):
#     """Class for postgres to ETL migration aimed to migrate
#     film_work table  by updated_at"""
#
#     def migrate(self, film_work_query: str, state_filed_name: str):
#         try:
#             with self.conn_postgres.cursor() as cursor:
#                 logger.debug('FilmWorkProcess.migrate_film_work() -> MainProcess._film_work_process()')
#                 self._film_work_process(
#                     cursor=cursor,
#                     film_work_query=film_work_query,
#                     state_field_name=state_filed_name,
#                 )
#         except (OperationalError, DatabaseError) as e:
#             logger.exception(e)
#
#     def _film_work_process(self, cursor, film_work_query, state_field_name):
#         logger.debug(f'MainProcess._film_work_process()')
#
#         def pg_producer():
#             return self.loader_process.postgres_producer(
#                 cursor=cursor,
#                 query=film_work_query,
#                 state_field_name=state_field_name
#             )
#
#         for loaded in iter(pg_producer, []):
#             logger.info(f'query results {len(loaded)=}')
#
#             parsed_data = self.transform_data.handle_merge_cases(query_result=loaded)
#             self._es_upload_batch(data=parsed_data)
#
#             self.state.validate_save_timestamp(
#                 state_field_name=state_field_name, timestamp=loaded[-1]["updated_at"]
#             )
from ..config_validation.indexes import FilmWork


class FilmWorkProcess(UnifiedProcess):
    validation_model = FilmWork
