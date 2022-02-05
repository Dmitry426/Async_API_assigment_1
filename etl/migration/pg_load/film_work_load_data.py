from etl.logger import logger
from etl.state.state_operator import StateOperator


class FilmWorkLoadData:
    def __init__(self, config):
        self.config_limit = config.limit
        self.state = StateOperator(config=config)
        self.film_work_ids = []

    def __handle_no_date(self, state_field_name: str):
        """Method to handle the case where we don't have recorded state yet."""
        limit = self.config_limit
        self.parsed_state = self.state.validate_load_timestamp(
            state_field_name=state_field_name
        )
        parsed_field = self.parsed_state[state_field_name]

        if not parsed_field:
            return f"ORDER BY updated_at LIMIT {limit}"

        if parsed_field and state_field_name == "film_work_updated_at":
            sql_query_params = f""" 
            WHERE fw.updated_at > ('{parsed_field}')
            ORDER BY updated_at
            LIMIT {limit};
            """
            return sql_query_params

        if parsed_field:
            sql_query_params = f""" 
               WHERE updated_at > ('{parsed_field}')
               ORDER BY updated_at
               LIMIT {limit};
            """
            return sql_query_params

    def postgres_producer(self, cursor, query: str, state_field_name: str):
        """Method to pg_load updated_at and ids from related to film_work fields"""
        date_limit = self.__handle_no_date(state_field_name=state_field_name)
        query_with_ids = query.format(date_limit)

        cursor.execute(query_with_ids)
        logger.info(f'LoadData.postgres_producer query\n{query_with_ids}')

        result = cursor.fetchall()
        return result

    def postgres_enricher(self, cursor, ids: str, query: str):
        """Method to pg_load related  film_work ids"""
        if ids:
            args = cursor.mogrify(query, (tuple(ids),))
            cursor.execute(args)
            fetch_fw_ids = cursor.fetchall()

            for data in dict(fetch_fw_ids):
                if data not in self.film_work_ids:
                    self.film_work_ids.append(data)

        return self.film_work_ids

    @staticmethod
    def postgres_merger(cursor, query: str, ids: list):
        """Method to pg_load from a table where table  ids matches your given ids"""
        args = cursor.mogrify(query, (tuple(ids),))
        cursor.execute(args)
        final_result = cursor.fetchall()
        return final_result
