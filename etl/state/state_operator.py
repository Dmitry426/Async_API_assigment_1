from etl.state.storages.json_file_storage import JsonFileStorage
from .state import State
from ..config_validation.utils import DatetimeSerialization


class StateOperator(State, JsonFileStorage):
    """
    Class to initialize state manger and validate 'updated_at' timestamp since json serializer
    does not serialize  DateTimeField with Timestamp by default.
    """

    def __init__(self, config):
        super().__init__(config)
        json_storage = JsonFileStorage(file_path=config.state_file_path)
        self.state = State(json_storage)
        self.updated_at = None

    def validate_load_timestamp(self, state_field_name: str):
        self.updated_at = self.state.get_state(key=state_field_name)
        parsed_time = DatetimeSerialization.parse_obj(
            {state_field_name: self.updated_at}
        ).dict()
        return parsed_time

    def validate_save_timestamp(self, state_field_name: str, timestamp: object):
        parsed_time = DatetimeSerialization.parse_obj(
            {state_field_name: timestamp}
        ).dict()
        self.state.set_state(
            key=state_field_name, value=str(parsed_time[state_field_name])
        )
