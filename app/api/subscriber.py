# third-party imports
import redis.asyncio as redis


from app.utils.logger import get_logger

logger = get_logger(__name__)

class Subscriber:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.pubsub = self.redis.pubsub()
    
    async def subscribe(self, channel):
        try:
            await self.pubsub.subscribe(channel)
        except Exception as e:
            logger.error(f"Error: Failed to subscribe to '{channel}': {e}")
        
    async def unsubscribe(self, channel):
        try:
            await self.pubsub.unsubscribe(channel)
        except Exception as e:
            logger.error(f"Error: Failed to unsubscribe '{channel}': {e}")
            
    async def close(self):
        await self.pubsub.close()
        await self.redis.close()
            
sub = Subscriber()