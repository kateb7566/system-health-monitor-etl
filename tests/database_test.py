import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from app.storage.database import get_db_session


@pytest.mark.asyncio
async def test_get_db_session_yields_session():
    mock_session = AsyncMock()
    # mock_context_manager = AsyncMock()
    # mock_context_manager.__aenter__.return_value = mock_session
    # mock_context_manager.__aexit__.return_value = None

    # Patch sessionmaker to return mock session
    with patch("app.storage.database.AsyncSessionLocal", return_value=AsyncMock(__aenter__ = AsyncMock(return_value=mock_session), __aexit__ = AsyncMock())):

        # `get_db_session` is an async generator, so we use `anext()` to get the yield
        gen = get_db_session()
        session = await anext(gen)

        assert session is mock_session
