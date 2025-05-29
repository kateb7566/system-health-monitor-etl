# test_real_time_ws.py
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect
from unittest.mock import AsyncMock, patch, MagicMock

from app.api.real_time_ws import router  # Replace with actual import path to your FastAPI app

app = FastAPI()
app.include_router(router)

client = TestClient(app)


@pytest.fixture
def mock_sub():
    mock_pubsub = AsyncMock()
    mock_pubsub.get_message = AsyncMock()

    mock_sub = MagicMock()
    mock_sub.subscribe = AsyncMock()
    mock_sub.unsubscribe = AsyncMock()
    mock_sub.close = AsyncMock()
    mock_sub.pubsub = mock_pubsub

    return mock_sub


def test_websocket_receives_message(mock_sub, monkeypatch):
    # Simulate one message and then timeout
    mock_sub.pubsub.get_message.side_effect = [
        {'data': 'test message', 'type': 'message'},
        None,
        WebSocketDisconnect()
    ]

    monkeypatch.setattr("app.api.real_time_ws.sub", mock_sub)

    with client.websocket_connect("/ws/metrics") as websocket:
        msg = websocket.receive_text()
        assert msg == "test message"

    mock_sub.subscribe.assert_awaited_once_with("metrics-channel")
    mock_sub.unsubscribe.assert_awaited_once_with("metrics-channel")
    mock_sub.close.assert_awaited_once()
