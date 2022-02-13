from functools import lru_cache
from typing import List, Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError
from elasticsearch_dsl import Search
from fastapi import Depends
from pydantic.validators import UUID

from db.elastic import get_elastic
from models.genre import Genre
from services.cache import RedisBackend, get_redis_backend_service


class GenreService:
    def __init__(self, redis: RedisBackend, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, genre_id: UUID) -> Optional[Genre]:
        genre = await self.redis.obj_from_cache(str(genre_id), Genre)

        if not genre:
            try:
                genre = await self._get_genre_from_elastic(genre_id)
            except NotFoundError:
                return None

            await self.redis.put_obj_to_cache(genre, str(genre.id))

        return genre

    async def get_list(self) -> List[Genre]:
        result = await self.redis.obj_from_cache("all_genres", Genre)
        if not result:
            search = Search(using=self.elastic).sort({"name.raw": "asc"})
            body = search.to_dict()
            data = await self.elastic.search(index="genres", body=body)
            result = [Genre(**hit["_source"]) for hit in data["hits"]["hits"]]

            if result:
                await self.redis.put_obj_to_cache(result, "all_genres")

        return result

    async def _get_genre_from_elastic(self, genre_id: UUID) -> Optional[Genre]:
        doc = await self.elastic.get("genres", genre_id)
        return Genre(**doc["_source"])


@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis_backend_service),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
