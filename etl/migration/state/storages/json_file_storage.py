import json
from json import JSONDecodeError
from pathlib import Path
from typing import Optional

from .base_storage import BaseStorage


class JsonFileStorage(BaseStorage):
    default_file_name = "state.json"

    def __init__(self, file_path: Optional[str] = None):
        self.file_path = file_path if file_path else self.default_file_name

        if not Path(self.file_path).exists():
            self.save_state({})

    def save_state(self, state: dict) -> None:
        with open(self.file_path, "w") as fp:
            json.dump(state, fp)

    def retrieve_state(self) -> dict:
        try:
            with open(self.file_path, "r") as fp:
                return json.load(fp)
        except FileNotFoundError:
            self.save_state(state={})
            return {}
        except JSONDecodeError:
            return {}
