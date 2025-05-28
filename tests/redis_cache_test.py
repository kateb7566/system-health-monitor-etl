import pytest
import json
from unittest.mock import AsyncMock, patch
from app.storage.redis_cache import CachePanel

@pytest.fixture
def mock_redis():
    mock = AsyncMock()
    mock.ttl.return_value = -1
    return mock

@pytest.fixture
def cache_panel(mock_redis):
    with patch("app.storage.redis_cache.redis.from_url", return_value=mock_redis):
        return CachePanel()


@pytest.mark.asyncio
async def test_cache_stores_data_and_sets_ttl(cache_panel):
    
    data = {"cpu": 10, "mem": 20}
    await cache_panel.cache(data)
    
    cache_panel.redis.rpush.assert_awaited_with("records", json.dumps(data))
    cache_panel.redis.ttl.assert_awaited_with("records")
    cache_panel.redis.expire.assert_awaited_with("records", 3600)


@pytest.mark.asyncio
async def test_get_cache_returns_data(cache_panel):
    mock_data = {"cpu": 50}
    cache_panel.redis.lindex.return_value = json.dumps(mock_data)
    
    result = await cache_panel.get_cache(0)
    assert result == mock_data
    cache_panel.redis.lindex.assert_awaited_with("records", 0)


@pytest.mark.asyncio
async def test_get_cache_returns_none_if_not_found(cache_panel):
    cache_panel.redis.lindex.return_value = None
    result = await cache_panel.get_cache(5)
    assert result is None


@pytest.mark.asyncio
async def test_get_all_cache_returns_all_items(cache_panel):
    raw = [json.dumps({"id": 1}), json.dumps({"id": 2})]
    cache_panel.redis.lrange.return_value = raw
    
    result = await cache_panel.get_all_cache()
    assert result == [{"id": 1}, {"id": 2}]
    cache_panel.redis.lrange.assert_awaited_with("records", 0, -1)


@pytest.mark.asyncio
async def test_cache_size_returns_length(cache_panel):
    cache_panel.redis.llen.return_value = 3
    result = await cache_panel.cache_size()
    assert result == 3
    cache_panel.redis.llen.assert_awaited_with("records")


@pytest.mark.asyncio
async def test_clear_cache_deletes_records(cache_panel):
    await cache_panel.clear_cache()
    cache_panel.redis.delete.assert_awaited_with("records")
