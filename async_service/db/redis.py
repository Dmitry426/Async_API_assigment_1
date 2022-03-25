from functools import lru_cache
from typing import Optional

import aioredis
from aioredis import Redis

from ..core.config import RedisSettings

redis_settings = RedisSettings()
redis: Optional[Redis] = None


@lru_cache
def get_redis() -> Redis:
    return aioredis.from_url(
        f"redis://{redis_settings.host}:{redis_settings.port}/{redis_settings.db}",
        encoding="utf8",
        decode_responses=True,
    )
