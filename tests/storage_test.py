import pytest
from unittest.mock import AsyncMock, MagicMock
from app.storage.storage import Storage

@pytest.fixture
def storage():
    return Storage()


@pytest.fixture
def fake_data():
    return {
        "time_stamp": "2023-01-01T00:00:00",
        "cpu_percent": 75,
        "memory": {"used": 1000},
        "disk": {"read": 100},
        "net_io": {"sent": 500}
    }


@pytest.mark.asyncio
async def test_save_to_db_success(storage, fake_data):
    db = AsyncMock()
    await storage.save_to_db(fake_data, db)
    db.add.assert_awaited()
    db.commit.assert_awaited()


@pytest.mark.asyncio
async def test_save_to_db_sqlalchemy_error(storage, fake_data):
    db = AsyncMock()
    
    # Simulate SQLAlchemyError during commit
    db.commit.side_effect = Exception("db error")
    await storage.save_to_db(fake_data, db)

    db.rollback.assert_awaited()


@pytest.mark.asyncio
async def test_get_data_from_db_success(storage):
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [{"mocked": "record"}]
    db.execute.return_value = mock_result

    result = await storage.get_data_from_db(db)
    assert result == [{"mocked": "record"}]


@pytest.mark.asyncio
async def test_get_data_from_db_failure(storage):
    db = AsyncMock()
    db.execute.side_effect = Exception("db error")
    result = await storage.get_data_from_db(db)
    assert result == []


@pytest.mark.asyncio
async def test_get_record_from_db_found(storage):
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = {"mocked": "record"}
    db.execute.return_value = mock_result

    record = await storage.get_record_from_db(db, 1)
    assert record == {"mocked": "record"}


@pytest.mark.asyncio
async def test_get_record_from_db_not_found(storage):
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_result

    record = await storage.get_record_from_db(db, 1)
    assert record is None
