from functools import lru_cache
from typing import List, Optional

from aioredis import Redis
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from elasticsearch_dsl import Q, Search
from fastapi import Depends
from models.film import Film
from pydantic.validators import UUID

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, film_id: str) -> Optional[Film]:
        film = await self._film_from_cache(film_id)

        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None
            await self._put_film_to_cache(film)

        return film

    async def get_list(
            self, sort: Optional[str], page_size: int, page_number: int, genre_id: Optional[UUID], query: Optional[str]
    ) -> List[Film]:

        search = Search(using=self.elastic)

        if query:
            search = search.query("multi_match", query=query, fields=["title, description"])

        if genre_id:
            search = search.query("nested", path="genres", query=Q("term", genres__id=genre_id))

        if sort:
            search = search.sort(sort)

        start = (page_number - 1) * page_size
        end = start + page_size

        result = await search[start:end].execute()

        return [Film(**hit.to_dict()) for hit in result]

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        doc = await self.elastic.get("movies", film_id)
        return Film(**doc["_source"])

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        data = await self.redis.get(film_id)
        if not data:
            return None

        film = Film.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: Film):
        await self.redis.set(film.id, film.json(), expire=FILM_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
