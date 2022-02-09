from typing import Any

from etl.state.storages.base_storage import BaseStorage


class State:
    def __init__(self, storage: BaseStorage):
        self.storage = storage

    def set_state(self, key: str, value: Any) -> None:
        load = self.storage.retrieve_state()
        load[key] = value

    def get_state(self, key: str) -> Any:
        result = self.storage.retrieve_state()
        if result and key in result.keys():
            return result[key]
        else:
            return None
