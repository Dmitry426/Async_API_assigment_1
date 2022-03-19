import os
from logging import config as logging_config


from dotenv import load_dotenv

from async_service import LOGGING

load_dotenv()

logging_config.dictConfig(LOGGING)

PROJECT_NAME = os.getenv("PROJECT_NAME", "movies")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT"))

ELASTIC_HOST = os.getenv("ELASTIC_HOST", "localhost")
ELASTIC_PORT = int(os.getenv("ELASTIC_PORT"))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

API_CACHE_TTL = int(os.getenv("API_CACHE_TTL", 3600))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
