import logging
import uuid
from datetime import datetime
from http import HTTPStatus

import pytest

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_genre_load_by_uuid(make_get_request, es_client, redis_client):
    genre_id: uuid = "ca124c76-9760-4406-bfa0-409b1e38d200"
    response = await make_get_request(method=f"/genre/{genre_id}")
    assert response.status == HTTPStatus.OK
    logger.debug("Response status : %s", response.status)
    assert response.body["name"] == "Biography"
    logger.info("Response Person name: %s", response.body["name"])


@pytest.mark.asyncio
async def test_genre_by_fake_uuid(make_get_request, es_client, redis_client):
    genre_id: uuid = uuid.uuid4()
    response = await make_get_request(method=f"/genre/{genre_id}")
    assert response.status == HTTPStatus.NOT_FOUND
    logger.debug("Response status : %s", response.status)


@pytest.mark.asyncio
async def test_if_genre_not_empty(make_get_request, es_client, redis_client):
    response = await make_get_request("/genre")
    assert response.status == HTTPStatus.OK
    logger.debug("Response status : %s", response.status)
    assert len(response.body) == 10
    logger.info("Response length : %s", len(response.body))


@pytest.mark.asyncio
async def test_redis_cash_genre(make_get_request, es_client, redis_client):
    await redis_client.flushdb()

    # empty redis call
    first_call_start = datetime.now()
    await make_get_request(method="/genre")
    first_call_duration = datetime.now() - first_call_start

    # redis has cash call
    second_call_start = datetime.now()
    await make_get_request(method="/genre")
    second_call_duration = datetime.now() - second_call_start

    logger.info("Call duration without cash : %s", first_call_duration)
    logger.info("Call duration with cash : %s", second_call_duration)
    assert first_call_duration >= second_call_duration

    await redis_client.flushdb()
