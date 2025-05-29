import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.api.subscriber import Subscriber

@pytest.fixture
def mock_redis_and_subscriber():
    
    mock_pubsub = AsyncMock()
    
    mock_redis_instance = MagicMock()
    mock_redis_instance.pubsub.return_value = mock_pubsub
    mock_redis_instance.close = AsyncMock()

    with patch("app.api.subscriber.redis.from_url", return_value=mock_redis_instance):
        subscriber = Subscriber()

        return subscriber, mock_redis_instance, mock_pubsub

@pytest.mark.asyncio
async def test_subscribe_success(mock_redis_and_subscriber):
    subscriber, _, mock_pubsub = mock_redis_and_subscriber
    await subscriber.subscribe("test_channel")
    mock_pubsub.subscribe.assert_awaited_once_with("test_channel")

@pytest.mark.asyncio
async def test_unsubscribe_success(mock_redis_and_subscriber):
    subscriber, _, mock_pubsub = mock_redis_and_subscriber
    await subscriber.unsubscribe("test_channel")
    mock_pubsub.unsubscribe.assert_awaited_once_with("test_channel")

@pytest.mark.asyncio
async def test_close_success(mock_redis_and_subscriber):
    subscriber, mock_redis_instance, mock_pubsub = mock_redis_and_subscriber
    await subscriber.close()
    mock_pubsub.close.assert_awaited_once()
    mock_redis_instance.close.assert_awaited_once()

@pytest.mark.asyncio
async def test_subscribe_error_logs(mock_redis_and_subscriber, caplog):
    subscriber, _, mock_pubsub = mock_redis_and_subscriber
    mock_pubsub.subscribe.side_effect = Exception("subscribe failed")

    with caplog.at_level("ERROR"):
        await subscriber.subscribe("bad_channel")

    assert "Error: Failed to subscribe to 'bad_channel': subscribe failed" in caplog.text

@pytest.mark.asyncio
async def test_unsubscribe_error_logs(mock_redis_and_subscriber, caplog):
    subscriber, _, mock_pubsub = mock_redis_and_subscriber
    mock_pubsub.unsubscribe.side_effect = Exception("unsubscribe failed")

    with caplog.at_level("ERROR"):
        await subscriber.unsubscribe("bad_channel")

    assert "Error: Failed to unsubscribe 'bad_channel': unsubscribe failed" in caplog.text
