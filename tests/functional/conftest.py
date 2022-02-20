import asyncio
import json
from dataclasses import dataclass

import aiofiles
import aiohttp
import aioredis
import pytest
from dotenv import load_dotenv
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from multidict import CIMultiDictProxy

from .core.settings import EsSettings, RedisSettings, UvicornURL
from .core.settings import TestSettings

load_dotenv()
ES_SETTINGS = EsSettings().dict()
REDIS_SETTINGS = RedisSettings().dict()
SERVICE_URL = UvicornURL().dict()

config = TestSettings.parse_file('./test_config.json')


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


@pytest.fixture(scope='session', name="es_client")
async def es_client():
    client = AsyncElasticsearch(hosts=f'http://{ES_SETTINGS["host"]}:{ES_SETTINGS["port"]}')
    yield client
    await client.close()


@pytest.fixture(scope='function')
def create_es_index(es_client):
    async def inner(index) -> str:
        if not await es_client.indices.exists(index=index):
            async with aiofiles.open(f'{config.index_path}/{index}.json') as file:
                data = await(file.read())
            result = json.loads(data)
            await es_client.indices.create(index=index, body=result)

    return inner


@pytest.fixture(scope='function')
def load_test_data(es_client):
    async def inner(index) -> str:
        if not await es_client.indices.exists(index=index):
            async with aiofiles.open(f'{config.data_path}/{index}.json') as file:
                data = await(file.read())
            result = json.loads(data)
            await async_bulk(es_client, result)

    return inner


@pytest.fixture(scope='function')
async def remove_es_data(es_client):

    yield None
    remove_index = []
    for index in config.es_indexes:
        if await es_client.indices.exists(index=index):
            remove_index.append(index)
    await es_client.indices.delete(index=remove_index)


@pytest.fixture(scope='session')
async def redis_connection():
    redis = await aioredis.create_redis_pool(
        (REDIS_SETTINGS['host'], REDIS_SETTINGS['port']), minsize=10, maxsize=20
    )
    yield redis
    await redis.close()


@pytest.fixture(scope='session')
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
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
