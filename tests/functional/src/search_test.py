import pytest


@pytest.mark.asyncio
async def test_search_detailed(make_get_request, load_test_data, create_es_index):
    await create_es_index('movies')
    await load_test_data('film')
    response = await make_get_request('/film', {'search': 'star '})
    assert response.status == 200
    assert len(response.body) == 5






