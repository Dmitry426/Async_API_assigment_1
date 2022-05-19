import logging

import uvicorn

from async_service import app
from async_service.core.logger import LOGGING

from .core.config import UvicornURL

url_settings = UvicornURL()

uvicorn.run(
    app,
    host=url_settings.host,
    port=url_settings.port,
    log_config=LOGGING,
    log_level=logging.DEBUG,
)
