import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import status, FastAPI
from unittest.mock import AsyncMock, patch

from app.api.routes import router   # Or whatever your FastAPI app instance is named

from app.models.models import Metrics

test_app = FastAPI()
test_app.include_router(router)

@pytest.mark.asyncio
@patch("app.storage.storage.Storage.get_data_from_db", new_callable=AsyncMock)
async def test_get_records(mock_get_data):
    mock_data = [
        Metrics(id=1, timestamp="2025-05-21T14:00:00", cpu_percent=12.5,
                memory={"total": 16000, "used": 8000}, 
                disk={"total": 500000, "used": 250000}, 
                net_io={"sent": 1000, "recv": 2000})
    ]
    mock_get_data.return_value = mock_data

    async with AsyncClient(transport=ASGITransport(router), base_url="http://test") as ac:
        response = await ac.get("/records")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]["id"] == 1


@pytest.mark.asyncio
@patch("app.storage.storage.Storage.get_record_from_db", new_callable=AsyncMock)
async def test_get_record_found(mock_get_record):
    mock_record = Metrics(id=1, timestamp="2025-05-21T14:00:00", cpu_percent=12.5,
                          memory={"total": 16000, "used": 8000}, 
                          disk={"total": 500000, "used": 250000}, 
                          net_io={"sent": 1000, "recv": 2000})
    mock_get_record.return_value = mock_record

    async with AsyncClient(transport=ASGITransport(router), base_url="http://test") as ac:
        response = await ac.get("/record/1")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == 1


@pytest.mark.asyncio
@patch("app.storage.storage.Storage.get_record_from_db", new_callable=AsyncMock)
async def test_get_record_not_found(mock_get_record):
    mock_get_record.return_value = None

    async with AsyncClient(transport=ASGITransport(router), base_url="http://test") as ac:
        response = await ac.get("/record/999")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Record not found!"}
