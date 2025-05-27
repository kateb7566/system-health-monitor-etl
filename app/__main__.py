# use load environment variables from .env file

# call ingestion layer manually
from app.ingest.fetcher import Fetcher
from app.storage.storage import Storage
from app.storage.database import get_db_session
from app.transform.transformer import Transformer
from app.utils.logger import get_logger
import asyncio
from fastapi import FastAPI
from app.api.routes import router as api_router
from app.api.real_time_ws import listen_channel as ws_router

app = FastAPI()

app.include_router(api_router)
app.include_router(ws_router)

logger = get_logger(__name__)

async def main():
    fetcher = Fetcher()
    transformer = Transformer()
    storage = Storage()
    
    try:
        logger.info("Starting async data pipeline...")
        data = await fetcher.run() # Fetch Data
        if data: # if data object does exist!
            transformed_data = transformer.transform(data) # Transform data
            async with get_db_session() as session:
                for item in transformed_data:
                    await storage.save_to_db(item, session) # save data
                    await storage.cache_to_redis(item) # save item to cache for easy recovery
            logger.info("Data saved successfully.")
        else:
            logger.warning("No data fetched.")
    except Exception as e:
        logger.exception(f"Pipeline failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())