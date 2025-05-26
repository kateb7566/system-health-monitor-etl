# Third-party imports
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext import SQLAlchemyError
from sqlalchemy.future import select

# Built-in imports
import json

# local imports
from app.config import settings
from app.utils.logger import get_logger
from app.models.models import MetricsModel

logger = get_logger(__name__)

class Storage:
    def __init__(self):
        pass
    
    async def save_to_db(self, data: dict, db: AsyncSession):
        try:
            record = MetricsModel(
                time_stamp = data['time_stamp'],
                cpu_percent = float(data['cpu_percent']),
                memory = json.dumps(data['memory']),
                disk = json.dumps(data['disk']),
                net_io = json.dumps(data['net_io'])
            )
            await db.add(record)
            await db.commit()
            logger.info(f"Record saved to DB")
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
    
    async def get_data_from_db(self, db: AsyncSession):
        try:
            result = await db.execute(select(MetricsModel))
            return result.scalars().all()
        except Exception as e:
            logger.error(f'Error fetching data from DB: {e}')
            return []
    
    async def get_record_from_db(self, db: AsyncSession, record_id: int):
        result = await db.execute(select(MetricsModel)).where(MetricsModel.id == record_id)
        record = result.scalar_one_or_none()
        if not record:
            logger.warning("record could not be retrieved!")
            return None
        logger.info("Record has been retrieved!")
        return record
    
storage = Storage()