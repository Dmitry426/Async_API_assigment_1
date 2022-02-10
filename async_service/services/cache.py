import json
from functools import lru_cache
from typing import List, Type, Union

from aioredis import Redis
from db.redis import get_redis
from fastapi import Depends
from pydantic import BaseModel


class RedisBackend:
    CACHE_EXPIRE_IN_SECONDS = 60 * 5

    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def obj_from_cache(self, obj_id: str, obj_type: Type[BaseModel]) -> Union[BaseModel, List[BaseModel], None]:
        data = await self.redis.get(obj_id)
        if not data:
            return None

        data = json.loads(data)

        if isinstance(data, list):
            obj = [obj_type.parse_raw(item) for item in data]
        else:
            obj = obj_type(**data)

        return obj

    async def put_obj_to_cache(self, obj: Union[BaseModel, List[BaseModel]], cache_key: str):
        if isinstance(obj, list):
            value = json.dumps([item.json() for item in obj])
        else:
            value = obj.json()

        await self.redis.set(cache_key, value, expire=self.CACHE_EXPIRE_IN_SECONDS)


@lru_cache
def get_redis_backend_service(redis: Redis = Depends(get_redis)) -> RedisBackend:
    return RedisBackend(redis)
