import pytest


@pytest.mark.asyncio
async def test_search_detailed(make_get_request):
    response = await make_get_request('/search', {'search': 'Star Wars'})
    assert response.status == 404
    assert len(response.body) == 1
