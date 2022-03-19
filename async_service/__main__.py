import logging
import os

import uvicorn
from async_service import app, LOGGING

uvicorn.run(
        app,
        host=os.environ.get("UVICORN_HOST"),
        port=os.environ.get("UVICORN_PORT"),
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
