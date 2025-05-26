# Third-party imports
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

# Built-in imports
from datetime import datetime

Base = declarative_base()

# SQLAlchemy Model
class MetricsModel(Base):
    __tablename__ = "resources"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    time_stamp = Column(DateTime, nullable=False)
    cpu_percent = Column(String, nullable=False)
    memory = Column(String, nullable=False)
    disk = Column(String, nullable=False)
    net_io = Column(String, nullable=False)
    
# Pydantic Schema
class Metrics(BaseModel):
    id: int = Field(..., description="Unique identifier of the Metrics model")
    time_stamp: datetime = Field(..., description="Timestamp of the taken out metrics!", alias="timestamp")
    cpu_percent: dict = Field(..., description="CPU percentage")
    memory: dict = Field(..., description="Memory Usage - RAM")
    disk: dict = Field(..., description="Disk Usage")
    net_io: dict = Field(..., description="Net IO Usage")
    
    class Config:
        orm_mode = True