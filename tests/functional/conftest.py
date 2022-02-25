import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Any, Dict

import aiofiles
import aiohttp
import aioredis
import elasticsearch
import pytest_asyncio
from dotenv import load_dotenv
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from multidict import CIMultiDictProxy

from .core.settings import EsSettings, RedisSettings, TestSettings, UvicornURL

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
es_logger = elasticsearch.logger
es_logger.setLevel(elasticsearch.logging.WARNING)

load_dotenv()
ES_SETTINGS = EsSettings().dict()
REDIS_SETTINGS = RedisSettings().dict()
SERVICE_URL = UvicornURL().dict()

config = TestSettings.parse_file("./test_config.json")


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


def generate_data(index: str, data: Dict) -> Dict:
    for item in data:
        yield dict(_index=index, _id=item["id"], _source=item)


async def remove_es_indexes(elastic_client):
    remove_index = []
    for index in config.es_indexes:
        if await elastic_client.indices.exists(index=index):
            remove_index.append(index)
    await elastic_client.indices.delete(index=remove_index)


async def load_json_data(file_path: str, index: str) -> Dict[str, Any]:
    async with aiofiles.open(f"{file_path}/{index}.json") as file:
        data = await (file.read())
    result = json.loads(data)
    return result


async def load_test_data(elastic_client: AsyncElasticsearch, index: str):
    result = await load_json_data(file_path=config.data_path, index=index)
    await async_bulk(elastic_client, generate_data(index, result))
    await asyncio.sleep(1)


async def create_es_index(elastic_client: AsyncElasticsearch, index: str):
    if not await elastic_client.indices.exists(index=index):
        result = await load_json_data(file_path=config.index_path, index=index)
        await elastic_client.indices.create(index=index, body=result)
    await asyncio.sleep(1)


@pytest_asyncio.fixture(scope="session", name="es_client")
async def es_client() -> AsyncElasticsearch:
    client = AsyncElasticsearch(
        hosts=f'http://{ES_SETTINGS["host"]}:{ES_SETTINGS["port"]}'
    )
    for index in config.es_indexes:
        await create_es_index(elastic_client=client, index=index)
        await load_test_data(elastic_client=client, index=index)
    yield client
    # await remove_es_indexes(elastic_client=client)
    await client.close()


@pytest_asyncio.fixture(name="redis_client", scope="session")
async def redis_client_fixture() -> aioredis:
    redis = aioredis.from_url(
        f"redis://{REDIS_SETTINGS['host']}:{REDIS_SETTINGS['port']}",
        encoding="utf8",
        decode_responses=True,
    )
    yield redis
    await redis.flushall()
    await redis.close()


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def session():
    session_aio = aiohttp.ClientSession()
    yield session_aio
    await session_aio.close()


@pytest_asyncio.fixture(scope="function")
def make_get_request(session):
    async def inner(method: str, params: dict = None) -> HTTPResponse:
        params = params or {}
        url = f'http://{SERVICE_URL["host"]}:{SERVICE_URL["port"]}{config.api_path}{method}'
        async with session.get(url, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )

    return inner
