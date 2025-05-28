# Third-party imports
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker

# local imports
from app.config import settings

DB_URL = settings.DB_URL

engine = create_async_engine(DB_URL, echo=True)


# Create an async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency-like context manager
async def get_db_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session