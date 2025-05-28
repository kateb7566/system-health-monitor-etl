# Third-Party imports
import redis.asyncio as redis

from app.utils.logger import get_logger

logger = get_logger(__name__)

class Publisher:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = redis.from_url(redis_url, decode_responses=True)
    
    async def publish(self, channel: str, message: str) -> None:
        try:
            await self.redis.publish(channel, message)
            logger.info(f"Published message to channel '{channel}'")
        except Exception as e:
            logger.error(f"Failed to publish message: {e}")

publisher = Publisher()