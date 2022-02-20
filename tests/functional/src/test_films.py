import pytest


@pytest.mark.asyncio
async def test_load_by_uuid(make_get_request, load_test_data, create_es_index):
    await create_es_index('movies')
    await load_test_data('film')
    response = await make_get_request('/film', '00e2e781-7af9-4f82-b4e9-14a488a3e184')
    assert response.status == 200
    assert len(response.body) == 5
    assert response.body[0]['imdb_rating'] == 6.5
    assert response.body[0]['title'] == "Star Slammer"
