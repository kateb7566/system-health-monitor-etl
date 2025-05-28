# test_fetcher.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
import json
from app.ingest.fetcher import Fetcher, logger  # Adjust import path as needed

class TestFetcher:
    @pytest.fixture
    def mock_settings(self):
        """Mock the settings module"""
        with patch('app.ingest.fetcher.settings') as mock:
            mock.API_ENDPOINT = "http://test.com"
            mock.API_KEY = "test-key"
            mock.REQUEST_TIMEOUT = 5
            mock.MAX_RETRIES = 3
            mock.RETRY_BACKOFF = 1
            yield mock

    @pytest.fixture
    def mock_publisher(self):
        """Mock the publisher instance"""
        with patch('app.ingest.fetcher.pub') as mock:
            mock.publish = AsyncMock()
            yield mock

    @pytest.fixture
    def mock_psutil(self):
        """Mock psutil methods"""
        with patch('app.ingest.fetcher.psutil') as mock:
            # Setup return values
            mock.cpu_percent.return_value = 25.5
            mock.virtual_memory.return_value = MagicMock(
                _asdict=lambda: {"total": 100, "used": 50}
            )
            mock.disk_usage.return_value = MagicMock(
                _asdict=lambda: {"total": 500, "used": 250}
            )
            mock.net_io_counters.return_value = MagicMock(
                _asdict=lambda: {"bytes_sent": 1000, "bytes_recv": 2000}
            )
            yield mock

    @pytest.fixture
    def fetcher(self, mock_settings, mock_publisher, mock_psutil):
        """Fixture providing a Fetcher instance with mocked dependencies"""
        return Fetcher()

    @pytest.mark.asyncio
    async def test_fetch_metrics_success(self, fetcher, mock_psutil, caplog):
        """Test successful metrics collection"""
        metrics = await fetcher.fetch_metrics()
        
        # Verify psutil calls
        mock_psutil.cpu_percent.assert_called_once_with(interval=None)
        mock_psutil.virtual_memory.assert_called_once()
        mock_psutil.disk_usage.assert_called_once_with('/')
        mock_psutil.net_io_counters.assert_called_once()
        
        # Verify metrics structure
        assert isinstance(metrics, dict)
        assert "timestamp" in metrics
        assert metrics["cpu_percent"] == 25.5
        assert metrics["memory"]["total"] == 100
        assert "the system data has been successfully collected!" in caplog.text

    @pytest.mark.asyncio
    async def test_fetcher_success(self, fetcher, mock_publisher, mock_psutil):
        """Test successful fetcher execution with publishing"""
        result = await fetcher.fetcher()
        
        # Verify metrics were published
        mock_publisher.publish.assert_awaited_once()
        args, _ = mock_publisher.publish.call_args
        assert args[0] == "metrics-channel"
        published_data = json.loads(args[1])
        assert published_data["cpu_percent"] == 25.5
        
        # Verify return value
        assert result == published_data

    @pytest.mark.asyncio
    async def test_fetcher_retry_success(self, fetcher, mock_publisher, mock_psutil):
        """Test retry mechanism with eventual success"""
        # First call fails, second succeeds
        mock_publisher.publish.side_effect = [
            Exception("First error"),
            AsyncMock()  # Success
        ]
        
        result = await fetcher.fetcher()
        
        # Should have retried once
        assert mock_publisher.publish.call_count == 2
        assert result is not None

    @pytest.mark.asyncio
    async def test_fetcher_all_retries_fail(self, fetcher, mock_publisher, caplog):
        """Test when all retry attempts fail"""
        mock_publisher.publish.side_effect = Exception("Persistent error")
        
        result = await fetcher.fetcher()
        
        # Should have retried MAX_RETRIES times
        assert mock_publisher.publish.call_count == fetcher.retries
        assert result is None
        assert "all collection attempts have failed!" in caplog.text

    @pytest.mark.asyncio
    async def test_run_method(self, fetcher, mock_publisher):
        """Test the run method delegates to fetcher"""
        mock_publisher.publish.return_value = None
        result = await fetcher.run()
        mock_publisher.publish.assert_awaited_once()
        assert result is not None

    @pytest.mark.asyncio
    async def test_metrics_timestamp_format(self, fetcher, mock_psutil):
        """Test timestamp format in metrics"""
        metrics = await fetcher.fetch_metrics()
        try:
            datetime.fromisoformat(metrics["timestamp"])
        except ValueError:
            pytest.fail("Timestamp is not in valid ISO format")