# test_websocket.py
import pytest
from fastapi import WebSocket, WebSocketDisconnect
from unittest.mock import AsyncMock, MagicMock, patch
from app.api.real_time_ws import router, SERVER_URL, logger  # Adjust import path as needed

@pytest.fixture
def mock_subscriber():
    with patch('app.api.subscriber.Subscriber') as mock:
        mock.subscribe = AsyncMock()
        mock.unsubscribe = AsyncMock()
        mock.close = AsyncMock()
        mock.pubsub = AsyncMock()
        yield mock

@pytest.fixture
def mock_websocket():
    ws = AsyncMock(spec=WebSocket)
    ws.accept = AsyncMock()
    ws.send_text = AsyncMock()
    return ws

@pytest.mark.asyncio
class TestWebSocketMetrics:
    async def test_websocket_connection_success(self, mock_subscriber, mock_websocket):
        """Test successful WebSocket connection and message handling"""
        # Setup mock behavior
        mock_subscriber.pubsub.get_message.side_effect = [
            None,  # First call returns no message
            {'data': 'test message', 'type': 'message'},  # Second call returns message
            WebSocketDisconnect()  # Third call simulates disconnect
        ]

        # Execute the WebSocket endpoint
        with pytest.raises(WebSocketDisconnect):
            await router.websocket("/ws/metrics")(mock_websocket)

        # Verify connection handling
        mock_websocket.accept.assert_awaited_once()
        mock_subscriber.subscribe.assert_awaited_once_with("metrics-channel")

        # Verify message handling
        mock_websocket.send_text.assert_awaited_once_with('test message')

        # Verify cleanup on disconnect
        mock_subscriber.unsubscribe.assert_awaited_once_with("metrics-channel")
        mock_subscriber.close.assert_awaited_once()

    async def test_websocket_immediate_disconnect(self, mock_subscriber, mock_websocket):
        """Test immediate WebSocket disconnect"""
        mock_subscriber.pubsub.get_message.side_effect = WebSocketDisconnect()

        with pytest.raises(WebSocketDisconnect):
            await router.websocket("/ws/metrics")(mock_websocket)

        mock_subscriber.subscribe.assert_awaited_once()
        mock_subscriber.unsubscribe.assert_awaited_once()
        mock_subscriber.close.assert_awaited_once()
        mock_websocket.send_text.assert_not_called()

    async def test_websocket_message_processing(self, mock_subscriber, mock_websocket):
        """Test multiple message processing"""
        test_messages = [
            {'data': 'msg1', 'type': 'message'},
            {'data': 'msg2', 'type': 'message'},
            WebSocketDisconnect()
        ]
        mock_subscriber.pubsub.get_message.side_effect = test_messages

        with pytest.raises(WebSocketDisconnect):
            await router.websocket("/ws/metrics")(mock_websocket)

        assert mock_websocket.send_text.await_count == 2
        mock_websocket.send_text.assert_any_await('msg1')
        mock_websocket.send_text.assert_any_await('msg2')

    async def test_websocket_ignore_subscribe_messages(self, mock_subscriber, mock_websocket):
        """Test that subscribe messages are ignored"""
        mock_subscriber.pubsub.get_message.side_effect = [
            {'type': 'subscribe'},  # Should be ignored
            {'data': 'real message', 'type': 'message'},
            WebSocketDisconnect()
        ]

        with pytest.raises(WebSocketDisconnect):
            await router.websocket("/ws/metrics")(mock_websocket)

        mock_websocket.send_text.assert_awaited_once_with('real message')

    async def test_websocket_error_handling(self, mock_subscriber, mock_websocket, caplog):
        """Test error during message processing"""
        mock_subscriber.pubsub.get_message.side_effect = Exception("Test error")

        with pytest.raises(Exception, match="Test error"):
            await router.websocket("/ws/metrics")(mock_websocket)

        assert "Error in WebSocket connection" in caplog.text