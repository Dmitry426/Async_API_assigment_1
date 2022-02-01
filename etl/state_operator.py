from validation_classes import Datetime_serialization
import abc
import json
from typing import Any, Optional


class BaseStorage:
    def __init__(self, file_path: Optional[str] = None):
        self.file_path = file_path

    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        with open(self.file_path, "w") as fp:
            json.dump(state, fp)

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        try:
            with open(self.file_path, "r") as fp:
                data = json.load(fp)
            return data
        except FileNotFoundError:
            self.save_state(state={})
            return {}


class JsonFileStorage(BaseStorage):
    pass


class State:
    def __init__(self, storage: BaseStorage):
        self.storage = storage

    def set_state(self, key: str, value: Any) -> None:
        load = self.storage.retrieve_state()
        load[key] = value
        self.storage.save_state(load)

    def get_state(self, key: str) -> Any:
        result = self.storage.retrieve_state()
        if result and key in result.keys():
            return result[key]
        else:
            return None


class State_operator(State, JsonFileStorage):
    """Class to initialize state manger and validate 'updated_at' timestamp since json serializer
    does not serialize  DateTimeField with Timestamp by default."""

    def __init__(self, config):
        self.file_path = config.state_file_path
        self.json_file_storage = JsonFileStorage(file_path=self.file_path)
        self.state = State(self.json_file_storage)
        self.updated_at = None

    def validate_load_timestamp(self, state_field_name: str):
        self.updated_at = self.state.get_state(key=state_field_name)
        parsed_time = Datetime_serialization.parse_obj(
            {state_field_name: self.updated_at}
        ).dict()
        return parsed_time

    def validate_save_timestamp(self, state_field_name: str, timestamp: object):
        parsed_time = Datetime_serialization.parse_obj(
            {state_field_name: timestamp}
        ).dict()
        self.state.set_state(
            key=state_field_name, value=str(parsed_time[state_field_name])
        )
