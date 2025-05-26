# third-party imports
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


# Built-in imports
from typing import List

# local imports
from app.models.models import Metrics, MetricsModel
from app.storage.database import get_db_session
from app.storage.storage import storage
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

@router.get("/records", response_model=List[Metrics], tags=["Metrics"])
async def get_records(db: AsyncSession = Depends(get_db_session)):
    logger.info("Retrieving data...")
    return await storage.get_data_from_db(db)

@router.get("/record/{record_id}", response_model=Metrics, tags=["Metrics"])
async def get_record(record_id: int, db: AsyncSession = Depends(get_db_session)):
    result = await storage.get_record_from_db(db, record_id)
    if result is None:
        logger.warning(f"Warning: record with ID {record_id} has not been found!")
        raise HTTPException(status_code=404, detail="Record not found!")
    logger.info(f"The record with Id {record_id} has been retrieved!")
    return result