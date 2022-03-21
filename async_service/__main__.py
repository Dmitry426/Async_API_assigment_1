import logging
import os

import uvicorn

from async_service import app
from async_service.core.logger import LOGGING

uvicorn.run(
    app,
    host=os.environ.get("UVICORN_HOST"),
    port=os.environ.get("UVICORN_PORT"),
    log_config=LOGGING,
    log_level=logging.DEBUG,
)
