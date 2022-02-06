from etl.logger import logger
from etl.config_validation.indexes import FilmWork


class FilmWorkDataMerger:
    def __init__(self):
        logger.debug('DataMerger.init()')
        self.desired_structure = {
            "id": "",
            "imdb_rating": "",
            "genre": [],
            "genres": [],
            "title": "",
            "description": "",
            'director': [],
            "directors": [],
            "actors_names": [],
            "writers_names": [],
            "writers": [],
            "actors": [],
        }
        self.results = []

    def combine_tables(self, obj: dict):
        logger.debug('DataMerger.combine_tables()')
        """Merges multiple tables into one dict"""
        self.desired_structure["id"] = obj["film_id"]
        self.desired_structure["imdb_rating"] = obj["rating"]
        self.desired_structure["title"] = obj["title"]
        self.desired_structure["description"] = obj["description"]
        self.__merging_conditions(obj=obj)

    def validate_and_return(self):
        """Validates data and returns dataclass obj"""
        logger.debug('DataMerger.validate_and_return()')
        validated_result = FilmWork.parse_obj(self.desired_structure)
        self.__empty_dataset()
        return validated_result

    def handle_merge_cases(self, query_result: list):
        """Method to data_merge datatables by id ,since Data is requested using Left Joins"""
        logger.debug('DataMerger.handle_merge_cases()')

        for index, element in enumerate(query_result):
            if index + 1 < len(query_result):
                if element["film_id"] == query_result[index + 1]["film_id"]:
                    self.combine_tables(element)
                    continue

            self.combine_tables(element)
            result = self.validate_and_return()
            self.results.append(result.dict())

        return self.results

    def __merging_conditions(self, obj: dict):
        """Merging conditions for actors, directors and writes fields"""
        if obj["genre"] not in self.desired_structure["genre"]:
            self.desired_structure["genre"].append(obj["genre"]),
            self.desired_structure["genres"].append(
                {"id": obj["genre_id"], "genre": obj["genre"]}
            )

        if (
                obj["role"] == "director"
                and obj["full_name"] not in self.desired_structure["director"]
        ):
            self.desired_structure["director"].append(obj["full_name"])
            self.desired_structure["directors"].append(
                {"id": obj["person_id"], "name": obj["full_name"]}
            )

        if (
                obj["role"] == "actor"
                and obj["full_name"] not in self.desired_structure["actors_names"]
        ):
            self.desired_structure["actors_names"].append(obj["full_name"]),
            self.desired_structure["actors"].append(
                {"id": obj["person_id"], "name": obj["full_name"]}
            )
        if (
                obj["role"] == "writer"
                and obj["full_name"] not in self.desired_structure["writers_names"]
        ):
            self.desired_structure["writers_names"].append(obj["full_name"]),
            self.desired_structure["writers"].append(
                {"id": obj["person_id"], "name": obj["full_name"]}
            )

    def __empty_dataset(self):
        """Method to empty merged dict"""
        self.desired_structure = {
            "id": "",
            "imdb_rating": "",
            "genre": [],
            "genres": [],
            "title": "",
            "description": "",
            'director': [],
            "directors": [],
            "actors_names": [],
            "writers_names": [],
            "writers": [],
            "actors": [],
        }
