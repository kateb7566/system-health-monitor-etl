# test_publisher.py
import pytest
from unittest.mock import AsyncMock, patch
from app.ingest.publisher import Publisher, logger  # Adjust import path as needed

class TestPublisher:
    @pytest.fixture
    def mock_redis(self):
        # Create an async mock for Redis
        return AsyncMock()
    
    @pytest.fixture
    def publisher(self, mock_redis):
        # Patch the Redis instance with our mock
        with patch('redis.asyncio.from_url', return_value=mock_redis) as _:
            return Publisher("redis://test:6379")
    
    @pytest.mark.asyncio
    async def test_publish_success(self, publisher, mock_redis, caplog):
        """Test successful message publishing"""
        # Setup mock behavior
        mock_redis.publish.return_value = 1  # Return number of subscribers
        
        # Execute
        await publisher.publish("test_channel", "test_message")
        
        # Verify Redis interaction
        mock_redis.publish.assert_awaited_once_with("test_channel", "test_message")
        
        # Verify logging
        assert "Published message to channel 'test_channel'" in caplog.text
    
    @pytest.mark.asyncio
    async def test_publish_failure(self, publisher, mock_redis, caplog):
        """Test failed message publishing"""
        # Setup mock to raise exception
        mock_redis.publish.side_effect = Exception("Redis connection error")
        
        # Execute and verify exception is handled
        await publisher.publish("test_channel", "test_message")
        
        # Verify logging
        assert "Failed to publish message: Redis connection error" in caplog.text
    
    @pytest.mark.asyncio
    async def test_redis_connection_params(self):
        """Test Redis connection parameters"""
        with patch('redis.asyncio.from_url') as mock_from_url:
            redis_url = "redis://custom:6380"
            _ = Publisher(redis_url)
            
            # Verify Redis connection parameters
            mock_from_url.assert_called_once_with(
                redis_url,
                decode_responses=True
            )
    
    @pytest.mark.asyncio
    async def test_default_redis_url(self):
        """Test default Redis URL is used when not specified"""
        with patch('redis.asyncio.from_url') as mock_from_url:
            _ = Publisher()
            
            # Verify default Redis URL
            mock_from_url.assert_called_once_with(
                "redis://localhost:6379",
                decode_responses=True
            )