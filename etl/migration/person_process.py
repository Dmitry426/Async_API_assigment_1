from datetime import datetime

from psycopg2 import DatabaseError, OperationalError

from etl.config_validation.indexes import Person
from etl.logger import logger
from etl.migration.main_process import MainProcess, UnifiedProcess


# class PersonProcess(MainProcess):
#     def migrate(self, producer_data, order_field, state_field):
#         # state loaded in MainProcess
#         try:
#             updated_person_ids = self.__get_updated_person_ids(producer_data)
#             rich_data = self.enrich_data(updated_person_ids)
#             ready_data = self.transform(rich_data)
#             self._es_upload_batch(ready_data)
#
#         except (OperationalError, DatabaseError) as e:
#             logger.exception(e)
#         except Exception as e:
#             logger.exception(e)
#
#     def enrich_data(self, person_ids):
#         with self.conn_postgres.cursor() as cursor:
#             query = self.config.enricher_query.format(ids=tuple(person_ids))
#             cursor.execute(cursor.mogrify(query))
#             enriched_data = cursor.fetchall()
#             return enriched_data
#
#     @staticmethod
#     def transform(persons):
#         return [Person.parse_obj(person).dict() for person in persons]
#
#     def __handle_no_date(self, query_data) -> str:
#         self.state.validate_load_timestamp(f'{query_data.table}_updated_at')
#         latest_value = self.state.updated_at if self.state.updated_at else datetime.min.isoformat()
#
#         sql_query_params = f"""WHERE {query_data.state_field} > ('{latest_value}')"""
#         return sql_query_params
#
#     def __get_updated_person_ids(self, producer_data):
#         with self.conn_postgres.cursor() as cursor:
#             persons = set()
#             for data in producer_data:
#                 query_tail = self.__handle_no_date(data)
#                 query = ' '.join([data.query, query_tail])
#
#                 mogrify_query = cursor.mogrify(query)
#                 cursor.execute(mogrify_query)
#                 query_data = cursor.fetchall()
#                 persons.update(person[0] for person in query_data)
#
#                 # save state
#                 latest_date = max(person[1] for person in query_data)
#             return persons

class PersonProcess(UnifiedProcess):
    validation_model = Person
