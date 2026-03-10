import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock
from app.http_client import Client
from app.tokens import OAuth2Token


@pytest.fixture
def client():
    c = Client()
    future = int((datetime.now(tz=timezone.utc) + timedelta(minutes=10)).timestamp())
    c.oauth2_token = OAuth2Token(access_token="any-token", expires_at=future)
    return c


def test_header_added_for_dict_token(client):
    client.oauth2_token = {"access_token": "any-value"}
    with patch.object(client.session, "send", return_value=MagicMock()) as mock_send:
        client.request("GET", "/dynamic-path", api=True)
        headers = mock_send.call_args[0][0].headers
        assert headers["Authorization"] == "Bearer fresh-token"


def test_refresh_not_called_before_expiry_buffer(client):
    buffer_seconds = 100
    now = int(datetime.now(tz=timezone.utc).timestamp())
    client.oauth2_token = OAuth2Token(access_token="any-token", expires_at=now + buffer_seconds)

    with patch.object(client, "refresh_oauth2") as mock_refresh:
        with patch.object(client.session, "send", return_value=MagicMock()):
            client.request("GET", "/dynamic-path", api=True)
            mock_refresh.assert_not_called()


def test_url_slash_added(client):
    path_without_slash = "users"
    with patch.object(client.session, "send", return_value=MagicMock()) as mock_send:
        client.request("GET", path_without_slash, api=True)
        prepared_req = mock_send.call_args[0][0]
        assert prepared_req.path_url.startswith("/")


def test_request_is_sent(client):
    sent_flag = {"called": False}

    def fake_send(req, **kwargs):
        sent_flag["called"] = True
        return MagicMock()

    with patch.object(client.session, "send", side_effect=fake_send):
        client.request("GET", "/dynamic-path", api=True)
        assert sent_flag["called"] is True