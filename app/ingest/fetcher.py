# imports
import asyncio
from datetime import datetime
import psutil

# local imports
from app.utils.logger import get_logger
from app.config import settings

logger = get_logger(__name__)

class Fetcher:
    def __init__(self):
        self.api_endpoint = settings.API_ENDPOINT
        self.api_key = settings.API_KEY
        self.timeout = settings.REQUEST_TIMEOUT
        self.retries = settings.MAX_RETRIES
        self.retry_backoff = settings.RETRY_BACKOFF
        self.metrics = {}
        
        
    async def fetch_metrics(self) -> dict:
        """Collect system metrics using psutil"""
        
        logger.info("the system data has been successfully collected!")
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "cpu_percent": psutil.cpu_percent(interval=None),
            "memory": psutil.virtual_memory()._asdict(),
            "disk": psutil.disk_usage('/')._asdict(),
            "net_io": psutil.net_io_counters()._asdict()
        }
        
    async def fetcher(self) -> dict | None:
        """Try to fetch metrics with retries on failure."""
        retries = 0
        while retries < self.retries:
            try:
                # get system health data
                metrics = await self.system_data()
                return metrics
            except Exception as e:
                logger.error(f"attempt {retries}: Could not get data! {e}")
                retries += 1
                await asyncio.sleep(self.retry_backoff * retries)
        logger.error("Unfortunately, all collection attempts have failed!")
        return None
    
    async def run(self) -> dict | None:
        return await self.fetcher()