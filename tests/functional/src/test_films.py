import logging
from http import HTTPStatus

import pytest

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_if_not_empty(make_get_request, es_client, redis_client):
    response = await make_get_request('/film')
    assert response.status == HTTPStatus.OK
    logger.debug('Response status : %s', response.status)
    assert response.body
    logger.info("Response length : %s", len(response.body))


@pytest.mark.asyncio
async def test_query_with_params(make_get_request, es_client, redis_client):
    page_size = 10
    response = await make_get_request(
        method='/film',
        params={'page[size]': page_size, 'page[number]': 1})
    assert response.status == HTTPStatus.OK
    logger.debug('Response status : %s', response.status)
    assert len(response.body) == page_size
    logger.info("Response length : %s", len(response.body))


@pytest.mark.asyncio
async def test_query_with_params_wrong(make_get_request, es_client, redis_client):
    response = await make_get_request(
        method='/film',
        params={'pagessdize': "sdaD"})
    assert response.status == HTTPStatus.ok
    logger.debug('Response status : %s', response.status)
    assert len(response.body)
    logger.info("Response length : %s", len(response.body))


@pytest.mark.asyncio
async def test_search_detailed(make_get_request, es_client, redis_client):
    response = await make_get_request('/film', {'search': 'star '})
    assert response.status == HTTPStatus.OK
    logger.debug('Response status : %s', response.status)
    assert len(response.body) == 50
    logger.info("Response length : %s", len(response.body))


@pytest.mark.asyncio
async def test_search_no_query(make_get_request, es_client, redis_client):
    response = await make_get_request('/film', {'search': ''})
    assert response.status == HTTPStatus.OK
    logger.debug('Response status : %s', response.status)
    assert len(response.body) == 50
    logger.info("Response length : %s", len(response.body))


@pytest.mark.asyncio
async def test_sort_success(make_get_request, es_client, redis_client):
    response = await make_get_request(
        method='/film',
        params={'page[size]': 50, 'page[number]': 1, 'sort': '-imdb_rating'})
    assert response.status == HTTPStatus.OK
    logger.debug('Response status : %s', response.status)
    assert response.body[0]["imdb_rating"] == 9.2
    logger.info("Response length : %s", response.body[0]["imdb_rating"])


@pytest.mark.asyncio
async def test_sort_by_genre_success(make_get_request, es_client, redis_client):
    genre_id = "55c723c1-6d90-4a04-a44b-e9792040251a"
    response = await make_get_request(
        method='/film',
        params={'page[size]': 50, 'page[number]': 1})
    assert response.status == HTTPStatus.OK
    logger.debug('Response status : %s', response.status)
    assert response.body[0]
    logger.info("Response length : %s", response.body[0])


@pytest.mark.asyncio
async def test_load_by_uuid(make_get_request, es_client):
    film_id = 'ec0399e9-abcd-46b7-94d9-f1d8a6c515e9'
    response = await make_get_request(f'/film/{film_id}')
    assert response.status == 200
    logger.debug('Response status : %s', response.status)
    assert response.body['title'] == "You're a Star"
