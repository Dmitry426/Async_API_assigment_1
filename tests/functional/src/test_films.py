import logging
import uuid
from datetime import datetime
from http import HTTPStatus

import pytest

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_if_not_empty(make_get_request, es_client, redis_client):
    response = await make_get_request("/film")
    assert response.status == HTTPStatus.OK
    logger.debug("Response status : %s", response.status)
    assert response.body
    logger.info("Response length : %s", len(response.body))


@pytest.mark.asyncio
async def test_film_query_with_params(make_get_request, es_client, redis_client):
    page_size = 10
    response = await make_get_request(
        method="/film", params={"page[size]": page_size, "page[number]": 1}
    )
    assert response.status == HTTPStatus.OK
    logger.debug("Response status : %s", response.status)
    assert len(response.body) == page_size
    logger.info("Response page size : %s", len(response.body))


@pytest.mark.asyncio
async def test_film_query_with_params_wrong(make_get_request, es_client, redis_client):
    response = await make_get_request(method="/film", params={"pagessdize": "sdaD"})
    assert response.status == HTTPStatus.OK
    logger.debug("Response status : %s", response.status)
    assert len(response.body) == 50
    logger.info("Response length : %s", len(response.body))


@pytest.mark.asyncio
async def test_film_search_detailed(make_get_request, es_client, redis_client):
    search_query: str = "star"
    response = await make_get_request(
        method="/film/search", params={"query": f"{search_query}"}
    )
    assert response.status == HTTPStatus.OK
    logger.debug("Response status : %s", response.status)
    assert len(response.body) == 50
    logger.info("Response length : %s", len(response.body))


@pytest.mark.asyncio
async def test_film_search_false_query(make_get_request, es_client, redis_client):
    search_query: str = "sfsjfsjf "
    response = await make_get_request(
        method="/film/search", params={"query": f"{search_query}"}
    )
    assert response.status == HTTPStatus.OK
    logger.debug("Response status : %s", response.status)
    assert len(response.body) == 0
    logger.info("Response length : %s", len(response.body))


@pytest.mark.asyncio
async def test_film_sort_success(make_get_request, es_client, redis_client):
    response = await make_get_request(
        method="/film",
        params={"page[size]": 50, "page[number]": 1, "sort": "-imdb_rating"},
    )
    assert response.status == HTTPStatus.OK
    logger.debug("Response status : %s", response.status)
    assert response.body[0]["imdb_rating"] == 9.2
    logger.info("Response Imdb rating max : %s", response.body[0]["imdb_rating"])


@pytest.mark.asyncio
async def test_sort_by_genre_success(make_get_request, es_client, redis_client):
    genre_id = "55c723c1-6d90-4a04-a44b-e9792040251a"
    response = await make_get_request(
        method="/film",
        params={"page[size]": 10, "page[number]": 1, "filter[genre]": f"{genre_id}"},
    )
    assert response.status == HTTPStatus.OK
    logger.debug("Response status : %s", response.status)
    assert len(response.body) == 6
    logger.info("Response length : %s", len(response.body))


@pytest.mark.asyncio
async def test_film_load_by_uuid(make_get_request, es_client, redis_client):
    film_id: uuid = "ec0399e9-abcd-46b7-94d9-f1d8a6c515e9"
    response = await make_get_request(method=f"/film/{film_id}")
    assert response.status == HTTPStatus.OK
    logger.debug("Response status : %s", response.status)
    assert response.body["title"] == "You're a Star"
    logger.info("Response title: %s", response.body["title"])


@pytest.mark.asyncio
async def test_film_by_fake_uuid(make_get_request, es_client, redis_client):
    film_id: uuid = uuid.uuid4()
    response = await make_get_request(method=f"/film/{film_id}")
    assert response.status == HTTPStatus.NOT_FOUND
    logger.debug("Response status : %s", response.status)


@pytest.mark.asyncio
async def test_redis_cash_film(make_get_request, es_client, redis_client):
    page_size: int = 50
    await redis_client.flushdb()

    # empty redis call
    first_call_start = datetime.now()
    await make_get_request(
        method="/film", params={"page[size]": page_size, "page[number]": 1}
    )
    first_call_duration = datetime.now() - first_call_start

    # redis has cash call
    second_call_start = datetime.now()
    await make_get_request(
        method="/film", params={"page[size]": page_size, "page[number]": 1}
    )
    second_call_duration = datetime.now() - second_call_start

    logger.info("Call duration without cash : %s", first_call_duration)
    logger.info("Call duration with cash : %s", second_call_duration)
    assert first_call_duration >= second_call_duration

    await redis_client.flushdb()
