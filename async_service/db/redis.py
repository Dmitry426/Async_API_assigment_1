from functools import lru_cache
from typing import Optional

import aioredis
from aioredis import Redis
from async_service.core import config

redis: Optional[Redis] = None


@lru_cache
def get_redis() -> Redis:
    return aioredis.from_url(
        f"redis://{config.REDIS_HOST}:{config.REDIS_PORT}/{config.REDIS_DB}",
        encoding="utf8",
        decode_responses=True,
    )
