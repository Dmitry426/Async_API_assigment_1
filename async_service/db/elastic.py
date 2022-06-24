from typing import Optional

from elasticsearch import AsyncElasticsearch

es: Optional[AsyncElasticsearch] = None


async def get_elastic() -> Optional[AsyncElasticsearch]:
    return es
