import json
from dataclasses import dataclass

import aiofiles
import aiohttp
import pytest
from dotenv import load_dotenv
from elasticsearch import AsyncElasticsearch
from multidict import CIMultiDictProxy

from .core.settings import EsSettings, RedisSettings, UvicornURL

load_dotenv()
ES_SETTINGS = EsSettings().dict()
REDIS_SETTINGS = RedisSettings.dict()
SERVICE_URL = UvicornURL().dict()


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


@pytest.fixture(scope='session')
async def load_data(path=str, data_name=str):
    async with aiofiles.open(f'{path}/{data_name}.json') as file:
        data = await(file.read())
    result = json.loads(data)
    return result


@pytest.fixture(scope='session', name="es_client")
async def es_client(load_data):
    client = AsyncElasticsearch([f"{ES_SETTINGS['host']}:{ES_SETTINGS['port']}"])
    yield client
    await client.close()


@pytest.fixture(scope='session')
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture
def make_get_request(session):
    async def inner(method: str, params: dict = None) -> HTTPResponse:
        params = params or {}
        url = f'http://{SERVICE_URL["host"]}:{SERVICE_URL["port"]}/api/v1{method}'
        async with session.get(url, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )

    return inner
