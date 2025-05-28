# test_subscriber.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.api.subscriber import Subscriber, logger  # Adjust import path as needed

class TestSubscriber:
    @pytest.fixture
    def mock_redis(self):
        """Mock Redis client and pubsub"""
        mock_redis = AsyncMock()
        mock_pubsub = AsyncMock()
        
        # Configure the mock chain
        mock_redis.from_url.return_value = mock_redis
        mock_redis.pubsub.return_value = mock_pubsub
        
        return mock_redis, mock_pubsub

    @pytest.fixture
    def subscriber(self, mock_redis):
        """Fixture providing a Subscriber instance with mocked Redis"""
        mock_client, _ = mock_redis
        with patch('redis.asyncio.from_url', return_value=mock_client):
            return Subscriber("redis://test:6379")

    @pytest.mark.asyncio
    async def test_subscribe_success(self, subscriber, mock_redis, caplog):
        """Test successful subscription"""
        _, mock_pubsub = mock_redis
        
        await subscriber.subscribe("test_channel")
        
        mock_pubsub.subscribe.assert_awaited_once_with("test_channel")
        assert "Error: Failed to subscribe" not in caplog.text

    @pytest.mark.asyncio
    async def test_subscribe_failure(self, subscriber, mock_redis, caplog):
        """Test failed subscription"""
        _, mock_pubsub = mock_redis
        mock_pubsub.subscribe.side_effect = Exception("Connection error")
        
        await subscriber.subscribe("test_channel")
        
        mock_pubsub.subscribe.assert_awaited_once_with("test_channel")
        assert "Error: Failed to subscribe to 'test_channel': Connection error" in caplog.text

    @pytest.mark.asyncio
    async def test_unsubscribe_success(self, subscriber, mock_redis, caplog):
        """Test successful unsubscription"""
        _, mock_pubsub = mock_redis
        
        await subscriber.unsubscribe("test_channel")
        
        mock_pubsub.unsubscribe.assert_awaited_once_with("test_channel")
        assert "Error: Failed to unsubscribe" not in caplog.text

    @pytest.mark.asyncio
    async def test_unsubscribe_failure(self, subscriber, mock_redis, caplog):
        """Test failed unsubscription"""
        _, mock_pubsub = mock_redis
        mock_pubsub.unsubscribe.side_effect = Exception("Connection error")
        
        await subscriber.unsubscribe("test_channel")
        
        mock_pubsub.unsubscribe.assert_awaited_once_with("test_channel")
        assert "Error: Failed to unsubscribe 'test_channel': Connection error" in caplog.text

    @pytest.mark.asyncio
    async def test_close(self, subscriber, mock_redis):
        """Test connection closing"""
        mock_instance_redis, mock_pubsub = mock_redis
        
        # assign the mocks to the subscriber
        subscriber.pubsub = mock_pubsub
        subscriber.redis = mock_instance_redis
        
        await subscriber.close()
        
        mock_pubsub.close.assert_awaited_once()
        mock_instance_redis.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_default_redis_url(self):
        """Test default Redis URL is used when not specified"""
        with patch('redis.asyncio.from_url') as mock_from_url:
            mock_redis = AsyncMock()
            mock_pubsub = AsyncMock()
            mock_redis.pubsub.return_value = mock_pubsub
            mock_from_url.return_value = mock_redis
            
            sub = Subscriber()
            
            mock_from_url.assert_called_once_with(
                "redis://localhost:6379",
                decode_responses=True
            )

    @pytest.mark.asyncio
    async def test_custom_redis_url(self):
        """Test custom Redis URL is used when specified"""
        with patch('redis.asyncio.from_url') as mock_from_url:
            mock_redis = AsyncMock()
            mock_pubsub = AsyncMock()
            mock_redis.pubsub.return_value = mock_pubsub
            mock_from_url.return_value = mock_redis
            
            custom_url = "redis://custom-host:6380"
            sub = Subscriber(custom_url)
            
            mock_from_url.assert_called_once_with(
                custom_url,
                decode_responses=True
            )