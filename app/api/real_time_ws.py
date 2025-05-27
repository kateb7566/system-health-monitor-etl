# Third-Party imports
import redis.asyncio as redis
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

# built-in imports
import asyncio

# local imports
from app.utils.logger import get_logger
from app.ingest.fetcher import Fetcher
from app.api.subscriber import sub

logger = get_logger(__name__)

router = APIRouter()

SERVER_URL = "ws://localhost:8765"

@router.websocket("/ws/metrics")
async def listen_channel(websocket: WebSocket):
    await websocket.accept()
    await sub.subscribe("metrics-channel")
    
    try:
        while True:
            message = await sub.pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message:
                await websocket.send_text(message['data'])
            await asyncio.sleep(0.01)
    except WebSocketDisconnect:
        await sub.unsubscribe("metrics-channel")
        await sub.close()
