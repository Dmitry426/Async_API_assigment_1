import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

import aiofiles
import aioredis
import backoff
import elasticsearch
import jwt
import pytest
import pytest_asyncio
from aiohttp import ClientSession
from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from pydantic import BaseModel

from .settings import TestSettings

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
es_logger = elasticsearch.logger
es_logger.setLevel(elasticsearch.logging.WARNING)


class HTTPResponse(BaseModel):
    body: Any
    headers: Dict[str, Any]
    status: int


@pytest_asyncio.fixture(name="settings", scope="session")
def settings_fixture() -> TestSettings:
    return TestSettings()


def generate_data(index: str, data: Dict) -> Dict:
    for item in data:
        yield dict(_index=index, _id=item["id"], _source=item)


async def remove_es_indexes(elastic_client, settings: TestSettings):
    remove_index = []
    for index in settings.es_indexes:
        if await elastic_client.indices.exists(index=index):
            remove_index.append(index)
    await elastic_client.indices.delete(index=remove_index)


async def load_json_data(file_path: str, index: str) -> Dict[str, Any]:
    async with aiofiles.open(f"{file_path}/{index}.json") as file:
        data = await (file.read())
    result = json.loads(data)
    return result


async def load_test_data(
    elastic_client: AsyncElasticsearch, index: str, settings: TestSettings
):
    result = await load_json_data(file_path=settings.data_path, index=index)
    await async_bulk(elastic_client, generate_data(index, result))


async def create_es_index(
    elastic_client: AsyncElasticsearch, index: str, settings: TestSettings
):
    if not await elastic_client.indices.exists(index=index):
        result = await load_json_data(file_path=settings.index_path, index=index)
        await elastic_client.indices.create(index=index, body=result)
    await asyncio.sleep(0.5)


@pytest_asyncio.fixture(scope="session", name="es_client")
async def es_client(settings: TestSettings) -> AsyncElasticsearch:
    client = AsyncElasticsearch(
        hosts=f"http://{settings.es_settings.host}:{settings.es_settings.port}"
    )
    await wait_for_ping(client=client, settings=settings)
    for index in settings.es_indexes:
        await create_es_index(elastic_client=client, index=index, settings=settings)
        await load_test_data(elastic_client=client, index=index, settings=settings)
    yield client
    await remove_es_indexes(elastic_client=client, settings=settings)
    await client.close()


@pytest_asyncio.fixture(name="redis_client", scope="session")
async def redis_client_fixture(settings: TestSettings) -> aioredis:
    redis_url = f"{settings.redis_settings.host}:{settings.redis_settings.port}/{settings.redis_settings.db}"
    redis = aioredis.from_url(
        f"redis://{redis_url}",
        encoding="utf8",
        decode_responses=True,
    )
    await wait_for_ping(client=redis, settings=settings)
    yield redis
    await redis.flushall()
    await redis.close()


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(name="http_client", scope="session")
async def http_client_fixture(settings, redis_client, es_client) -> ClientSession:
    """Represents HTTP client fixture.

    Add dependency fixtures `postgres_client` and `redis_client` to
    check they are ready to work.
    """
    async with ClientSession(
        base_url=f"http://{settings.url_settings.host}:{settings.url_settings.port}"
    ) as session:
        yield session


async def wait_for_ping(
    client: Union[Redis, AsyncElasticsearch], settings: TestSettings
):
    """Wait for service client to answer"""
    client_name = type(client).__name__

    @backoff.on_exception(
        wait_gen=backoff.expo,
        exception=(RuntimeError, ConnectionError, TimeoutError),
        max_time=settings.ping_timeout,
    )
    async def _ping(inner_client):
        result = await inner_client.ping()
        if not result:
            raise RuntimeError(f"{client_name} still not ready...")

    return await _ping(client)


@pytest_asyncio.fixture(name="make_get_request", scope="session")
def make_get_request(http_client: ClientSession):
    """Make HTTP-request"""

    async def inner(
        url: str,
        params: Optional[Dict[str, Any]] = None,
        jwt: Optional[str] = None,
    ) -> HTTPResponse:
        params = params or {}
        headers = {}

        if jwt:
            headers = {"Authorization": "Bearer {}".format(jwt)}

        logger.debug("URL: %s", url)

        async with http_client.get(url, params=params, headers=headers) as response:
            body = await response.json()
            logger.warning("Response: %s", body)

            return HTTPResponse(
                body=body,
                headers=dict(response.headers),
                status=response.status,
            )

    return inner


@pytest.fixture(name="create_jwt_token", scope="function")
def create_jwt_token(settings: TestSettings):
    payload = {
        "type": "access",
        "exp": datetime.utcnow() + timedelta(days=0, minutes=30),
        "iat": datetime.utcnow(),
        "sub": {"roles": ["subscribed"]},
    }
    return jwt.encode(
        payload,
        settings.jwt_settings.secret_key,
        algorithm=settings.jwt_settings.algorithm,
    )
