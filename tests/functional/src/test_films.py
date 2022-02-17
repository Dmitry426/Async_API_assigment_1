import aiohttp
import pytest

from dataclasses import dataclass
from multidict import CIMultiDictProxy
from elasticsearch import AsyncElasticsearch




@pytest.mark.asyncio
async def test_search_detailed(make_get_request):
    response = await make_get_request('/search', {'search': 'Star Wars'})
    assert response.status == 200
    assert len(response.body) == 1

