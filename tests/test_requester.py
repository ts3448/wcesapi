import logging
import pytest
import requests
import requests_mock
import time
from datetime import datetime
from wcesapi.requester import (
    Requester,
    UnauthorizedAccess,
    ResourceDoesNotExist,
    UnprocessableEntity,
    RequesterError,
)


@pytest.fixture
def requester():
    return Requester(base_url="http://example.com", access_token="test_token")


def test_requester_initialization(requester):
    assert requester.base_url == "http://example.com/api/"
    assert requester.access_token == "test_token"
    assert requester.max_retries == 3
    assert requester.retry_backoff == 2
    assert requester.rate_limit_delay == 1


def test_set_retry_options(requester):
    requester.set_retry_options(max_retries=5, retry_backoff=3)
    assert requester.max_retries == 5
    assert requester.retry_backoff == 3


def test_set_rate_limit_delay(requester):
    requester.set_rate_limit_delay(rate_limit_delay=2)
    assert requester.rate_limit_delay == 2


@pytest.mark.parametrize("method", ["GET", "POST", "PUT", "DELETE", "PATCH"])
def test_successful_request(requester, method):
    with requests_mock.Mocker() as m:
        m.request(method, "http://example.com/api/test", json={"success": True})
        response = requester.request(method, "test")
        assert response == {"success": True}


@pytest.mark.parametrize(
    "status_code, exception",
    [
        (401, UnauthorizedAccess),
        (404, ResourceDoesNotExist),
        (422, UnprocessableEntity),
        (500, RequesterError),
    ],
)
def test_request_errors(requester, status_code, exception):
    with requests_mock.Mocker() as m:
        m.get(f"http://example.com/api/test", status_code=status_code)
        with pytest.raises(exception):
            requester.request("GET", "test")


def test_retry_on_rate_limit(requester, mocker):
    mock_handle_rate_limit = mocker.patch.object(requester, "_handle_rate_limit")
    with requests_mock.Mocker() as m:
        m.get(
            "http://example.com/api/test",
            [{"status_code": 429}, {"status_code": 429}, {"json": {"success": True}}],
        )
        response = requester.request("GET", "test")
        assert response == {"success": True}
        assert mock_handle_rate_limit.call_count == 2


def test_prepare_request_kwargs(requester):
    kwargs = requester._prepare_request_kwargs(
        params={"key": "value"}, data={"data_key": "data_value"}
    )
    assert kwargs == {"params": {"key": "value"}, "data": {"data_key": "data_value"}}
    assert (
        requester._session.headers["Content-Type"]
        == "application/x-www-form-urlencoded"
    )


def test_filter_none_values():
    data = {"a": 1, "b": None, "c": "test"}
    filtered = Requester._filter_none_values(data)
    assert filtered == {"a": 1, "c": "test"}


def test_format_value():
    assert Requester._format_value(True) == "true"
    assert Requester._format_value(False) == "false"
    assert Requester._format_value(datetime(2023, 1, 1)) == "2023-01-01T00:00:00"
    assert Requester._format_value("test") == "test"
    assert Requester._format_value(123) == "123"


def test_calculate_rate_limit_delay(requester):
    assert requester._calculate_rate_limit_delay(0) == 1
    assert requester._calculate_rate_limit_delay(1) == 2
    assert requester._calculate_rate_limit_delay(2) == 4

    requester.rate_limit_delay = 2
    requester.retry_backoff = 3
    assert requester._calculate_rate_limit_delay(0) == 2
    assert requester._calculate_rate_limit_delay(1) == 6


def test_handle_rate_limit(requester, mocker):
    mock_sleep = mocker.patch("time.sleep")
    mock_calculate = mocker.patch.object(
        requester, "_calculate_rate_limit_delay", return_value=5
    )

    requester._handle_rate_limit(1)
    mock_calculate.assert_called_once_with(1)
    mock_sleep.assert_called_once_with(5)


def test_log_response(requester, caplog):
    caplog.set_level(logging.INFO)
    with requests_mock.Mocker() as m:
        m.get("http://example.com/api/test", json={"success": True})
        requester.request("GET", "test")
    assert any(
        "Response: GET http://example.com/api/test 200" in record.message
        for record in caplog.records
    )


def test_parse_response(requester):
    mock_response = requests.Response()
    mock_response._content = b'{"key": "value"}'
    assert requester._parse_response(mock_response) == {"key": "value"}

    mock_response._content = b"Not JSON"
    assert requester._parse_response(mock_response) == {"raw_text": "Not JSON"}


def test_request_exception(requester):
    with requests_mock.Mocker() as m:
        m.get("http://example.com/api/test", exc=requests.RequestException)
        with pytest.raises(RequesterError):
            requester.request("GET", "test")


def test_max_retries_exceeded(requester):
    with requests_mock.Mocker() as m:
        m.get("http://example.com/api/test", status_code=429)
        with pytest.raises(RequesterError, match="Request failed after all retries"):
            requester.request("GET", "test")

