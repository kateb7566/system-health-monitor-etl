# Third-Party imports
import redis.asyncio as redis

# Built-in imports
import json

# Local imports
from app.models.models import MetricsModel, Metrics
from app.utils.logger import get_logger

logger = get_logger(__name__)

class CachePanel:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        
    async def cache(self, data: dict) -> None:
        try:
            await self.redis.rpush("records", json.dumps(data))
            ttl = await self.redis.ttl("records")
            if ttl == -1:
                await self.redis.expire("records", 3600)
            logger.info("Record pushed to Redis")
        except Exception as e:
            logger.error(f"Failed to push to Redis: {e}")
            
    async def get_cache(self, record_id: int) -> dict | None:
        try:
            data = await self.redis.lindex("records", record_id)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Failed to get record from Redis: {e}")
            return None
        
    async def get_all_cache(self) -> list[dict]:
        try:
            raw_data = await self.redis.lrange("records", 0, -1)
            return [json.loads(item) for item in raw_data]
        except Exception as e:
            logger.error(f"Failed to get all records from redis: {e}")
            return []
        
    async def cache_size(self) -> int:
        try:
            return await self.redis.llen("records")
        except Exception as e:
            logger.error(f"Failed to get Redis cache size: {e}")
            return 0
    
    async def clear_cache(self) -> None:
        try:
            await self.redis.delete("records")
            logger.info("Redis cache cleared.")
        except Exception as e:
            logger.error(f"Failed to clear Redis cache: {e}")
        