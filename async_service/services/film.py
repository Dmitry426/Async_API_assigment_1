from functools import lru_cache
from typing import List, Optional

from db.elastic import get_elastic
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError
from elasticsearch_dsl import Q, Search
from fastapi import Depends
from models.film import Film
from pydantic.validators import UUID

from services.cache import RedisBackend, get_redis_backend_service

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class FilmService:
    def __init__(self, redis: RedisBackend, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, film_id: UUID) -> Optional[Film]:
        film = await self.redis.obj_from_cache(str(film_id), Film)

        if not film:
            try:
                film = await self._get_film_from_elastic(film_id)
            except NotFoundError:
                film = None

            if not film:
                return None
            await self.redis.put_obj_to_cache(film, str(film.id))

        return film

    async def get_list(
            self, page_size: int, page_number: int, sort: Optional[str] = None,
            genre_id: Optional[UUID] = None, query: Optional[str] = None
    ) -> List[Film]:
        cache_key = f"{page_size}, {page_number}, {sort}, {genre_id}, {query}"
        result = await self.redis.obj_from_cache(cache_key, Film)

        if not result:
            search = Search(using=self.elastic)
            if query:
                search = search.query(Q("match", title={"query": query, "fuzziness": "auto"}))

            if genre_id:
                search = search.query("nested", path="genres", query=Q("term", genres__id=genre_id))

            if sort:
                search = search.sort(sort)

            start = (page_number - 1) * page_size
            end = start + page_size

            search = search[start:end]
            body = search.to_dict()
            data = await self.elastic.search(index="movies", body=body)
            result = [Film(**hit["_source"]) for hit in data["hits"]["hits"]]

            if result:
                await self.redis.put_obj_to_cache(result, cache_key)

        return result

    async def _get_film_from_elastic(self, film_id: UUID) -> Optional[Film]:
        doc = await self.elastic.get("movies", film_id)
        return Film(**doc["_source"])


@lru_cache()
def get_film_service(
        redis: RedisBackend = Depends(get_redis_backend_service),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
