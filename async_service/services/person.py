from functools import lru_cache
from typing import List, Optional

from aioredis import Redis
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError
from elasticsearch_dsl import Q, Search
from fastapi import Depends
from models.person import Person
from models.film import Film
from pydantic.validators import UUID

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, person_id: UUID) -> Optional[Person]:
        person = await self._person_from_cache(str(person_id))

        if not person:
            try:
                person = await self._get_person_from_elastic(person_id)
            except NotFoundError:
                person = None

            if not person:
                return None
            await self._put_person_to_cache(person)

        return person

    async def get_list(
            self, page_size: int, page_number: int,
            query: Optional[str] = None
    ) -> List[Person]:

        search = Search(using=self.elastic)
        if query:
            search = search.query(Q("multi_match", query=query, fields=['full_name', 'role'], fuzziness='auto'))

        start = (page_number - 1) * page_size
        end = start + page_size
        search = search[start:end]
        body = search.to_dict()
        result = await self.elastic.search(index="persons", body=body)

        return [Person(**hit["_source"]) for hit in result["hits"]["hits"]]

    async def get_films_by_person(self, page_size: int, page_number: int,
                                  person_id: UUID
                                  ) -> List[Film]:
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
        result = await self.elastic.search(index="movies", body=body)

        return [Film(**hit["_source"]) for hit in result["hits"]["hits"]]

    async def _get_person_from_elastic(self, person_id: UUID) -> Optional[Person]:
        doc = await self.elastic.get("persons", person_id)
        return Person(**doc["_source"])

    async def _person_from_cache(self, person_id: str) -> Optional[Person]:
        data = await self.redis.get(person_id)
        if not data:
            return None

        person = Person.parse_raw(data)
        return person

    async def _put_person_to_cache(self, person: Person):
        await self.redis.set(str(person.id), person.json(), expire=FILM_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
