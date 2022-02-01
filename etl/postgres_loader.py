from state_operator import State_operator


class Load_data:
    def __init__(self, config):
        self.state = State_operator(config=config)
        self.config = config
        self.film_work_ids = []

    def __handle_no_date(self, state_field_name: str):
        """Method to handle the case where we don't have recorded state yet."""
        limit = self.config.limit
        self.parsed_state = self.state.validate_load_timestamp(
            state_field_name=state_field_name
        )
        if self.parsed_state[state_field_name] is None:
            sql_query_params = f""" 
            ORDER BY updated_at
            LIMIT {limit};
        """
            return sql_query_params
        if (
            self.parsed_state[state_field_name]
            and state_field_name == "film_work_updated_at"
        ):
            sql_query_params = f""" 
            WHERE fw.updated_at > ('%s')
            ORDER BY updated_at
            LIMIT {limit};
        """ % (
                self.parsed_state[state_field_name]
            )
            return sql_query_params

        if self.parsed_state[state_field_name]:
            sql_query_params = f""" 
               WHERE updated_at > ('%s')
               ORDER BY updated_at
               LIMIT {limit};
           """ % (
                self.parsed_state[state_field_name]
            )
            return sql_query_params

    def postgres_producer(self, cursor, query: str, state_field_name: str):
        """Method to load updated_at and ids from related to film_work fields"""
        query_ids = query.format(
            self.__handle_no_date(state_field_name=state_field_name)
        )
        cursor.execute(query_ids)
        result = cursor.fetchall()
        return result

    def postgres_enricher(self, cursor, ids: str, query: str):
        """Method to load related  film_work ids"""
        if ids:
            args = cursor.mogrify(query, (tuple(ids),))
            cursor.execute(args)
            fetch_fw_ids = cursor.fetchall()
            for data in dict(fetch_fw_ids):
                if data not in self.film_work_ids:
                    self.film_work_ids.append(data)
        return self.film_work_ids

    def postgres_merger(self, cursor, query: str, ids: list):
        """Method to load from a table where table  ids matches your given ids"""
        args = cursor.mogrify(query, (tuple(ids),))
        cursor.execute(args)
        final_result = cursor.fetchall()
        return final_result
