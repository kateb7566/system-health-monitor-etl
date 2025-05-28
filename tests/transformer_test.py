import pytest
from datetime import datetime
from app.transform.transformer import Transformer

@pytest.fixture
def transformer():
    return Transformer()


def test_transform_returns_empty_list_on_none(transformer):
    result = transformer.transform(None)
    assert result == []


def test_transform_returns_empty_list_on_empty(transformer):
    result = transformer.transform([])
    assert result == []


def test_transform_valid_item(transformer):
    now = datetime.utcnow().isoformat()
    data = [{
        "timestamp": now,
        "cpu_percent": 50,
        "memory": 2048,
        "disk": 100,
        "net_io": "eth0"
    }]
    
    result = transformer.transform(data)
    assert len(result) == 1
    assert result[0]["time_stamp"] == now
    assert result[0]["cpu_percent"] == 50
    assert result[0]["memory"] == 2048
    assert result[0]["disk"] == 100
    assert result[0]["net_io"] == "eth0"


def test_transform_skips_invalid_item(transformer):
    # Missing memory and net_io
    data = [{
        "timestamp": datetime.utcnow().isoformat(),
        "cpu_percent": 20,
        "disk": 50
    }]
    result = transformer.transform(data)
    assert result == []


def test_parse_datetime_returns_valid(transformer):
    now = datetime.utcnow().isoformat()
    result = transformer.parse_datetime(now)
    assert result == now


def test_parse_datetime_handles_invalid(transformer):
    result = transformer.parse_datetime("not-a-date")
    # It falls back to utcnow().isoformat()
    assert isinstance(result, str)
    # We check if it at least parses back to datetime
    parsed = datetime.fromisoformat(result)
    assert isinstance(parsed, datetime)


def test_is_valid_true(transformer):
    item = {
        "time_stamp": "2023-01-01T00:00:00",
        "cpu_percent": 75,
        "memory": 8000,
        "disk": 200,
        "net_io": "eth0"
    }
    assert transformer.is_valid(item) is True


def test_is_valid_false(transformer):
    item = {
        "time_stamp": None,
        "cpu_percent": 75,
        "memory": 8000,
        "disk": 200,
        "net_io": "eth0"
    }
    assert transformer.is_valid(item) is False
