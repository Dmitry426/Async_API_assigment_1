import logging
import uuid
from datetime import datetime
from http import HTTPStatus

import pytest

logger = logging.getLogger(__name__)

PATH = "/api/v1/person"
pytestmark = pytest.mark.asyncio


class TestPerson:
    search_query: str = "James"
    person_name: str = "James Doohan"
    page_size: int = 50
    person_id: uuid = "8a01bb4e-207f-4549-a3f6-6892b1aac5a9"
    person_film: uuid = "78d65b0c-51b0-4e03-8c28-fda307bb9c34"

    async def test_person_search_detailed(self, make_get_request):
        response = await make_get_request(
            url=f"{PATH}/search", params={"query": f"{self.search_query}"}
        )
        assert response.status == HTTPStatus.OK
        logger.debug("Response status : %s", response.status)
        assert response.body[0]["full_name"] == self.person_name
        logger.info("Person name : %s ", response.body[0]["full_name"])

    async def test_person_load_by_uuid(self, make_get_request):
        response = await make_get_request(url=f"{PATH}/{self.person_id}")
        assert response.status == HTTPStatus.OK
        logger.debug("Response status : %s", response.status)
        assert response.body["full_name"] == "Nathalie Cox"
        logger.info("Response Person name: %s", response.body["full_name"])

    async def test_person_by_film(self, make_get_request):
        response = await make_get_request(
            url=f"{PATH}/{self.person_film}/film",
            params={"page[size]": 10, "page[number]": 1},
        )
        assert response.status == HTTPStatus.OK
        logger.debug("Response status : %s", response.status)
        assert response.body[0]["title"] == "The All Star Impressions Show"
        logger.info("Person film name : %s", response.body[0]["title"])

    async def test_redis_cash_person(self, make_get_request, es_client, redis_client):
        await redis_client.flushdb()

        # empty redis call
        first_call_start = datetime.now()
        await make_get_request(
            url=PATH, params={"page[size]": self.page_size, "page[number]": 1}
        )
        first_call_duration = datetime.now() - first_call_start

        # redis has cash call
        second_call_start = datetime.now()
        await make_get_request(
            url=PATH, params={"page[size]": self.page_size, "page[number]": 1}
        )
        second_call_duration = datetime.now() - second_call_start

        logger.info("Call duration without cash : %s", first_call_duration)
        logger.info("Call duration with cash : %s", second_call_duration)
        assert first_call_duration > second_call_duration

        await redis_client.flushdb()


class TestPersonNegative:
    search_query_misspell: str = "Jamesa"
    person_name: str = "James Doohan"
    search_query_fake: str = "WQFDSD"
    person_id_random: uuid = uuid.uuid4()

    async def test_person_search_wrong_spell(self, make_get_request):
        response = await make_get_request(
            url=f"{PATH}/search", params={"query": f"{self.search_query_misspell}"}
        )
        assert response.status == HTTPStatus.OK
        logger.debug("Response status : %s", response.status)
        assert response.body[0]["full_name"] == self.person_name
        logger.info("Person name : %s ", response.body[0]["full_name"])

    async def test_person_search_fail(self, make_get_request):
        response = await make_get_request(
            url=f"{PATH}/search", params={"query": f"{self.search_query_fake}"}
        )
        assert response.status == HTTPStatus.NOT_FOUND
        logger.debug("Response status : %s", response.status)
        assert response.body["detail"] == "The is no such person "
        logger.info("Response  : %s", response.body["detail"])

    async def test_person_by_fake_uuid(self, make_get_request):
        response = await make_get_request(url=f"{PATH}/{self.person_id_random}")
        assert response.status == HTTPStatus.NOT_FOUND
        logger.debug("Response status : %s", response.status)

    async def test_person_by_film_fake_uuid(self, make_get_request):
        response = await make_get_request(
            url=f"{PATH}/{self.person_id_random}/film",
            params={"page[size]": 1, "page[number]": 1},
        )
        assert response.status == HTTPStatus.OK
        logger.debug("Response status : %s", response.status)
        assert len(response.body) == 0
        logger.info("Response length : %s", len(response.body))
