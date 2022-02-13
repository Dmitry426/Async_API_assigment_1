from functools import lru_cache
from typing import List, Optional

from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError
from elasticsearch_dsl import Q, Search
from fastapi import Depends
from pydantic.validators import UUID

from db.elastic import get_elastic
from models.film import Film
from models.person import Person
from services.cache import RedisBackend, get_redis_backend_service


class PersonService:
    def __init__(self, redis: RedisBackend, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, person_id: UUID) -> Optional[Person]:
        person = await self.redis.obj_from_cache(str(person_id), Person)

        if not person:
            try:
                person = await self._get_person_from_elastic(person_id)
            except NotFoundError:
                return None

            await self.redis.put_obj_to_cache(person, str(person_id))

        return person

    async def get_list(
            self, page_size: int, page_number: int,
            query: Optional[str] = None
    ) -> List[Person]:
        cache_key = f"{page_size}, {page_number},  {query}"
        result = await self.redis.obj_from_cache(cache_key, Person)

        if not result:
            search = Search(using=self.elastic)
            if query:
                search = search.query(Q("multi_match", query=query, fields=['full_name', 'role'], fuzziness='auto'))

            start = (page_number - 1) * page_size
            end = start + page_size
            search = search[start:end]
            body = search.to_dict()
            data = await self.elastic.search(index="persons", body=body)
            result = [Person(**hit["_source"]) for hit in data["hits"]["hits"]]

            if result:
                await self.redis.put_obj_to_cache(result, cache_key)

        return result

    async def get_films_by_person(self, page_size: int, page_number: int,
                                  person_id: UUID
                                  ) -> List[Film]:
        cache_key = f"{page_size}, {page_number},  {person_id}"
        result = await self.redis.obj_from_cache(cache_key, Film)

        if not result:
            search = Search(using=self.elastic)
            search = search.query(Q("bool",
                                    should=[
                                        Q("nested", path="directors", query=Q("term", directors__id=person_id)),
                                        Q("nested", path="actors", query=Q("term", actors__id=person_id)),
                                        Q("nested", path="writers", query=Q("term", writers__id=person_id)),
                                    ]))
            start = (page_number - 1) * page_size
            end = start + page_size
            search = search[start:end]
            body = search.to_dict()
            data = await self.elastic.search(index="movies", body=body)
            result = [Film(**hit["_source"]) for hit in data["hits"]["hits"]]
            if result:
                await self.redis.put_obj_to_cache(result, cache_key)

        return result

    async def _get_person_from_elastic(self, person_id: UUID) -> Optional[Person]:
        doc = await self.elastic.get("persons", person_id)
        return Person(**doc["_source"])


@lru_cache()
def get_person_service(
        redis: RedisBackend = Depends(get_redis_backend_service),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
