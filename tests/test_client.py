import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

from app.http_client import Client
from app.tokens import OAuth2Token, token_from_iso

def test_token_expired_false():
    future_time = int((datetime.now(tz=timezone.utc) + timedelta(minutes=10)).timestamp())
    token = OAuth2Token(access_token="abc", expires_at=future_time)
    assert token.expired is False

def test_token_expired_true():
    past_time = int((datetime.now(tz=timezone.utc) - timedelta(minutes=1)).timestamp())
    token = OAuth2Token(access_token="abc", expires_at=past_time)
    assert token.expired is True

def test_token_as_header():
    token = OAuth2Token(access_token="abc123", expires_at=9999999999)
    assert token.as_header() == "Bearer abc123"

def test_token_from_iso_with_timezone():
    token = token_from_iso("abc123", "2030-01-01T12:00:00+00:00")
    assert isinstance(token, OAuth2Token)
    assert token.access_token == "abc123"
    assert token.expires_at == 1893470400

def test_token_from_iso_without_timezone():
    token = token_from_iso("abc123", "2030-01-01T12:00:00")
    assert token.expires_at == 1893470400

@patch("app.http_client.requests.Session.prepare_request")
def test_client_adds_auth_header(mock_prepare_request):
    client = Client()
    future_time = int((datetime.now(tz=timezone.utc) + timedelta(minutes=10)).timestamp())
    client.oauth2_token = OAuth2Token(access_token="token123", expires_at=future_time)

    mock_prepared_request = MagicMock()
    mock_prepared_request.headers = {"Authorization": "Bearer token123"}
    mock_prepare_request.return_value = mock_prepared_request

    result = client.request("GET", "/test-path", api=True)

    headers = result["headers"]
    assert "Authorization" in headers
    assert headers["Authorization"] == "Bearer token123"

@patch("app.http_client.Client.refresh_oauth2")
def test_client_refresh_called_when_token_expired(mock_refresh):
    client = Client()
    past_time = int((datetime.now(tz=timezone.utc) - timedelta(minutes=1)).timestamp())
    client.oauth2_token = OAuth2Token(access_token="old", expires_at=past_time)

    client.request("GET", "/test-path", api=True)

    mock_refresh.assert_called_once()

@patch("app.http_client.requests.Session.prepare_request")
def test_client_url_slash_added(mock_prepare_request):
    client = Client()
    future_time = int((datetime.now(tz=timezone.utc) + timedelta(minutes=10)).timestamp())
    client.oauth2_token = OAuth2Token(access_token="token123", expires_at=future_time)

    mock_prepared_request = MagicMock()
    mock_prepared_request.headers = {}
    mock_prepare_request.return_value = mock_prepared_request

    result = client.request("GET", "users", api=True)

    prepared_headers = result["headers"]

@patch("app.http_client.requests.Session.prepare_request")
def test_client_request_sent(mock_prepare_request):
    client = Client()
    future_time = int((datetime.now(tz=timezone.utc) + timedelta(minutes=10)).timestamp())
    client.oauth2_token = OAuth2Token(access_token="token123", expires_at=future_time)

    mock_prepared_request = MagicMock()
    mock_prepared_request.headers = {}
    mock_prepare_request.return_value = mock_prepared_request

    result = client.request("GET", "/dummy", api=True)

    mock_prepare_request.assert_called_once()