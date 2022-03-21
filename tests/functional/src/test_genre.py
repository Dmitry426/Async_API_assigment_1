import logging
import uuid
from datetime import datetime
from http import HTTPStatus

import pytest

logger = logging.getLogger(__name__)

PATH = "/api/v1/genre"
pytestmark = pytest.mark.asyncio


class TestGenre:
    genre_id: uuid = "ca124c76-9760-4406-bfa0-409b1e38d200"

    async def test_genre_load_by_uuid(self, make_get_request):
        response = await make_get_request(url=f"{PATH}/{self.genre_id}")
        assert response.status == HTTPStatus.OK
        logger.debug("Response status : %s", response.status)
        assert response.body["name"] == "Biography"
        logger.info("Response Person name: %s", response.body["name"])

    async def test_if_genre_not_empty(self, make_get_request):
        response = await make_get_request(url=PATH)
        assert response.status == HTTPStatus.OK
        logger.debug("Response status : %s", response.status)
        assert len(response.body) == 26
        logger.info("Response length : %s", len(response.body))

    async def test_redis_cash_genre(self, make_get_request, redis_client):
        await redis_client.flushdb()

        # empty redis call
        first_call_start = datetime.now()
        await make_get_request(url=PATH)
        first_call_duration = datetime.now() - first_call_start

        # redis has cash call
        second_call_start = datetime.now()
        await make_get_request(url=PATH)
        second_call_duration = datetime.now() - second_call_start

        logger.info("Call duration without cash : %s", first_call_duration)
        logger.info("Call duration with cash : %s", second_call_duration)
        assert first_call_duration > second_call_duration

        await redis_client.flushdb()


class TestGenreNegative:
    genre_id_random: uuid = uuid.uuid4()

    async def test_genre_by_fake_uuid(self, make_get_request):
        response = await make_get_request(url=f"{PATH}/{self.genre_id_random}")
        assert response.status == HTTPStatus.NOT_FOUND
        logger.debug("Response status : %s", response.status)
