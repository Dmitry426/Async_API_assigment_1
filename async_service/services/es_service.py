import logging
from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError
from elasticsearch_dsl import Search, Q

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class EsService(ABC):
    elastic_index_name: str
    response_model: BaseModel

    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    @property
    @abstractmethod
    def elastic_index_name(self) -> str:
        pass

    @property
    @abstractmethod
    def response_model(self):
        pass

    async def get_by_id(self, obj_id: UUID) -> Optional[BaseModel]:
        """Get from es by id """
        try:
            doc = await self.elastic.get(index=self.elastic_index_name, id=obj_id)

        except NotFoundError:
            logger.debug("Obj %s is not found", obj_id)
            return None
        return self.response_model(**doc["_source"])

    async def get_list_search(
            self, page_size: int, page_number: int,
            query: Optional[str] = None, sort: Optional[str] = None,
    ) -> List[BaseModel]:
        """Get from es search by query  """

        search = Search(using=self.elastic)
        if query:
            search = self._search_by_query(search=search, query=query)

        if sort:
            search = search.sort(sort)

        start = (page_number - 1) * page_size
        end = start + page_size
        search = search[start:end]
        body = search.to_dict()
        data = await self.elastic.search(index=self.elastic_index_name, body=body)
        result = [self.response_model(**hit["_source"]) for hit in data["hits"]["hits"]]

        return result

    async def get_list_filter_by_id(self, page_size: int, page_number: int,
                                    sort: str = None,
                                    genre_id: Optional[UUID] = None,
                                    person_id: Optional[UUID] = None
                                    ) -> List[BaseModel]:
        """Get from es search filter by uuid and sort """

        search = Search(using=self.elastic)
        if genre_id:
            search = search.query("nested", path="genres", query=Q("term", genres__id=genre_id))

        if person_id:
            search = search.query(Q("bool",
                                    should=[
                                        Q("nested", path="directors", query=Q("term", directors__id=person_id)),
                                        Q("nested", path="actors", query=Q("term", actors__id=person_id)),
                                        Q("nested", path="writers", query=Q("term", writers__id=person_id)),
                                    ]))
        if sort:
            search = search.sort(sort)

        start = (page_number - 1) * page_size
        end = start + page_size
        search = search[start:end]
        body = search.to_dict()
        data = await self.elastic.search(index=self.elastic_index_name, body=body)
        result = [self.response_model(**hit["_source"]) for hit in data["hits"]["hits"]]

        return result

    def _search_by_query(self, search: Search, query: str):
        """Method to separate search queries by index"""

        if self.elastic_index_name == "movies":
            search = search.query(Q("match", title={"query": query, "fuzziness": "auto"}))

            return search

        if self.elastic_index_name == "persons":
            search = search.query(Q("multi_match", query=query, fields=['full_name', 'role'], fuzziness='auto'))

            return search
