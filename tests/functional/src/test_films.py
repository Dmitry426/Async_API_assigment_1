import logging
import uuid
from datetime import datetime
from http import HTTPStatus

import pytest

logger = logging.getLogger(__name__)

PATH = "/api/v1/film"
pytestmark = pytest.mark.asyncio


class TestFilm:
    page_size =42
    search_query: str = "star"
    genre_id: uuid = "55c723c1-6d90-4a04-a44b-e9792040251a"
    film_id: uuid = "ec0399e9-abcd-46b7-94d9-f1d8a6c515e9"

    async def test_if_not_empty(self, make_get_request, es_client, redis_client):
        response = await make_get_request(url=PATH)
        assert response.status == HTTPStatus.OK
        logger.debug("Response status : %s", response.status)
        assert response.body
        logger.info("Response length : %s", len(response.body))

    async def test_film_query_with_params(self, make_get_request):
        response = await make_get_request(
            url=PATH, params={"page[size]": self.page_size, "page[number]": 1},
        )
        assert response.status == HTTPStatus.OK
        logger.debug("Response status : %s", response.status)
        assert len(response.body) == self.page_size
        logger.info("Response page size : %s", len(response.body))

    async def test_film_search_detailed(self, make_get_request):
        response = await make_get_request(
            url=f"{PATH}/search", params={"query": f"{self.search_query}"}
        )
        assert response.status == HTTPStatus.OK
        logger.debug("Response status : %s", response.status)
        assert len(response.body) == 42
        logger.info("Response length : %s", len(response.body))

    async def test_film_sort_success(self, make_get_request):
        response = await make_get_request(
            url=f"{PATH}",
            params={"page[size]": 50, "page[number]": 1, "sort": "-rating"},
        )
        assert response.status == HTTPStatus.OK
        logger.debug("Response status : %s", response.status)
        logger.debug("Response status : %s", response.status)
        assert response.body[0]["rating"] == 8.6
        logger.info("Response Imdb rating max : %s", response.body[0]["rating"])

    async def test_sort_by_genre_success(self, make_get_request):
        response = await make_get_request(
            url=PATH,
            params={
                "page[size]": 10,
                "page[number]": 1,
                "filter[genre]": f"{self.genre_id}",
            },
        )
        assert response.status == HTTPStatus.OK
        logger.debug("Response status : %s", response.status)
        assert len(response.body) == 2
        logger.info("Response length : %s", len(response.body))

    async def test_film_load_by_uuid(self, make_get_request):
        response = await make_get_request(url=f"{PATH}/{self.film_id}")
        assert response.status == HTTPStatus.OK
        logger.debug("Response status : %s", response.status)
        assert response.body["title"] == "You're a Star"
        logger.info("Response title: %s", response.body["title"])

    async def test_redis_cash_film(self, make_get_request, redis_client):
        page_size: int = 50
        await redis_client.flushdb()

        # empty redis call
        first_call_start = datetime.now()
        await make_get_request(
            url=PATH, params={"page[size]": page_size, "page[number]": 1}
        )
        first_call_duration = datetime.now() - first_call_start

        # redis has cash call
        second_call_start = datetime.now()
        await make_get_request(
            url=PATH, params={"page[size]": page_size, "page[number]": 1}
        )
        second_call_duration = datetime.now() - second_call_start

        logger.info("Call duration without cash : %s", first_call_duration)
        logger.info("Call duration with cash : %s", second_call_duration)
        assert first_call_duration > second_call_duration

        await redis_client.flushdb()


class TestsFilmNegative:
    search_query_fake: str = "sfsjfsjf "
    film_id_random: uuid = uuid.uuid4()

    async def test_film_query_with_params_wrong(self, make_get_request):
        response = await make_get_request(url=PATH, params={"pagessdize": "sdaD"})
        assert response.status == HTTPStatus.OK
        logger.debug("Response status : %s", response.status)
        assert len(response.body) == 42
        logger.info("Response length : %s", len(response.body))

    async def test_film_search_false_query(self, make_get_request):
        response = await make_get_request(
            url=f"{PATH}/search", params={"query": f"{self.search_query_fake}"}
        )
        assert response.status == HTTPStatus.OK
        logger.debug("Response status : %s", response.status)
        assert len(response.body) == 0
        logger.info("Response length : %s", len(response.body))

    async def test_film_by_fake_uuid(self, make_get_request):
        response = await make_get_request(url=f"{PATH}/{self.film_id_random}")
        assert response.status == HTTPStatus.NOT_FOUND
        logger.debug("Response status : %s", response.status)
