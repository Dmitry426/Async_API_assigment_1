from typing import Any

from etl.logger import logger
from etl.state.storages.base_storage import BaseStorage


class State:
    def __init__(self, storage: BaseStorage):
        logger.debug('State.init()')
        logger.debug(f'\t{storage=}')
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
