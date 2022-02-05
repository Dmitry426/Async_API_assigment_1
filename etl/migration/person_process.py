from psycopg2 import DatabaseError, OperationalError

from etl.logger import logger
from etl.migration.main_process import MainProcess


class PersonProcess(MainProcess):
    def migrate(self, producer_queries, order_field, state_field):
        logger.debug('PersonProcess.migrate()')

        try:
            with self.conn_postgres.cursor() as cursor:
                for query in producer_queries:
                    logger.debug(query)

        except (OperationalError, DatabaseError) as e:
            logger.exception(e)
