import json
from dataclasses import dataclass

import aiofiles
import aiohttp
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

config = TestSettings.parse_file('../test_config.json')


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


async def load_data(path, data_name) -> str:
    async with aiofiles.open(f'{path}/{data_name}.json') as file:
        data = await(file.read())
    result = json.loads(data)
    return result


@pytest.fixture(scope='session', name="es_client")
async def es_client():
    client = AsyncElasticsearch(hosts=f'http://{ES_SETTINGS["host"]}:{ES_SETTINGS["port"]}')
    yield client
    await client.close()


@pytest.fixture(scope='function')
def manage_elastic_data(es_client):
    async def inner(data_chunk, index) -> str:
        index_body = await load_data(path=config.index_path, data_name=index)
        await es_client.indices.create(index=index, body=index_body)
        result = await load_data(path=config.data_path, data_name=data_chunk)
        await async_bulk(es_client, result)

        yield result

        await es_client.indices.delete(index=index)

    return inner


@pytest.fixture(scope='session')
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


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
