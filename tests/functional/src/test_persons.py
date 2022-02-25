import logging
import uuid
from datetime import datetime
from http import HTTPStatus

import pytest

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_person_search_detailed(make_get_request, es_client, redis_client):
    search_query: str = "James"
    person_name: str = "James Doohan"
    response = await make_get_request(
        method="/person/search", params={"query": f"{search_query}"}
    )
    assert response.status == HTTPStatus.OK
    logger.debug("Response status : %s", response.status)
    assert response.body[0]["full_name"] == person_name
    logger.info("Person name : %s ", response.body[0]["full_name"])


@pytest.mark.asyncio
async def test_person_search_wrong_spell(make_get_request, es_client, redis_client):
    search_query: str = "Jamesa"
    person_name: str = "James Doohan"
    response = await make_get_request(
        method="/person/search", params={"query": f"{search_query}"}
    )
    assert response.status == HTTPStatus.OK
    logger.debug("Response status : %s", response.status)
    assert response.body[0]["full_name"] == person_name
    logger.info("Person name : %s ", response.body[0]["full_name"])


@pytest.mark.asyncio
async def test_person_search_fail(make_get_request, es_client, redis_client):
    search_query: str = "WQFDSD"
    response = await make_get_request(
        method="/person/search", params={"query": f"{search_query}"}
    )
    assert response.status == HTTPStatus.NOT_FOUND
    logger.debug("Response status : %s", response.status)
    assert response.body["detail"] == "The is no such person "
    logger.info("Response  : %s", response.body["detail"])


@pytest.mark.asyncio
async def test_person_load_by_uuid(make_get_request, es_client, redis_client):
    person_id: uuid = "8a01bb4e-207f-4549-a3f6-6892b1aac5a9"
    response = await make_get_request(method=f"/person/{person_id}")
    assert response.status == HTTPStatus.OK
    logger.debug("Response status : %s", response.status)
    assert response.body["full_name"] == "Nathalie Cox"
    logger.info("Response Person name: %s", response.body["full_name"])


@pytest.mark.asyncio
async def test_person_by_fake_uuid(make_get_request, es_client, redis_client):
    person_id: uuid = uuid.uuid4()
    response = await make_get_request(method=f"/person/{person_id}")
    assert response.status == HTTPStatus.NOT_FOUND
    logger.debug("Response status : %s", response.status)


@pytest.mark.asyncio
async def test_person_by_film(make_get_request, es_client, redis_client):
    page_size: int = 1
    person_id: uuid = "78d65b0c-51b0-4e03-8c28-fda307bb9c34"
    response = await make_get_request(
        method=f"/person/{person_id}/film",
        params={"page[size]": page_size, "page[number]": 1},
    )
    assert response.status == HTTPStatus.OK
    logger.debug("Response status : %s", response.status)
    assert response.body[0]["title"] == "The All Star Impressions Show"
    logger.info("Person film name : %s", response.body[0]["title"])


@pytest.mark.asyncio
async def test_person_by_film_fake_uuid(make_get_request, es_client, redis_client):
    page_size: int = 1
    person_id: uuid = uuid.uuid4()
    response = await make_get_request(
        method=f"/person/{person_id}/film",
        params={"page[size]": page_size, "page[number]": 1},
    )
    assert response.status == HTTPStatus.OK
    logger.debug("Response status : %s", response.status)
    assert len(response.body) == 0
    logger.info("Response length : %s", len(response.body))


@pytest.mark.asyncio
async def test_redis_cash_person(make_get_request, es_client, redis_client):
    page_size: int = 66
    await redis_client.flushdb()

    # empty redis call
    first_call_start = datetime.now()
    await make_get_request(
        method="/person", params={"page[size]": page_size, "page[number]": 1}
    )
    first_call_duration = datetime.now() - first_call_start

    # redis has cash call
    second_call_start = datetime.now()
    await make_get_request(
        method="/person", params={"page[size]": page_size, "page[number]": 1}
    )
    second_call_duration = datetime.now() - second_call_start

    logger.info("Call duration without cash : %s", first_call_duration)
    logger.info("Call duration with cash : %s", second_call_duration)
    assert first_call_duration >= second_call_duration

    await redis_client.flushdb()
