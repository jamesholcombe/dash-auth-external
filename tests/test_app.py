import pytest
from dash_auth_external import DashAuthExternal
from unittest.mock import Mock
from dash_auth_external.config import FLASK_SESSION_TOKEN_KEY
from .test_config import (
    EXERNAL_TOKEN_URL,
    EXTERNAL_AUTH_URL,
    CLIENT_ID,
    CLIENT_SECRET,
)
from requests_oauthlib import OAuth2Session


@pytest.mark.parametrize(
    "with_pkce, with_client_secret",
    [(True, True), (True, False), (False, True), (False, False)],
)
def test_flow(with_pkce, with_client_secret, mocker):

    auth = DashAuthExternal(
        EXTERNAL_AUTH_URL,
        EXERNAL_TOKEN_URL,
        CLIENT_ID,
        with_pkce=with_pkce,
        client_secret=CLIENT_SECRET if with_client_secret else None,
    )
    redirect_uri = "http://127.0.0.1:8050" + auth.redirect_suffix

    session_mock = Mock(
        OAuth2Session(
            CLIENT_ID,
            redirect_uri=redirect_uri,
            scope=auth.scope,
        )
    )
    app = auth.server
    session_mock.authorization_url.return_value = ("https://example.com", "state")

    mocker.patch("dash_auth_external.routes.OAuth2Session", return_value=session_mock)
    token_request_mock = mocker.patch(
        "dash_auth_external.routes.token_request",
        return_value={
            "access_token": "access_token",
            "refresh_token": "refresh_token",
            "token_type": "Bearer",
            "expires_in": "3599",
        },
    )
    expected_token_request_body = {
        "grant_type": "authorization_code",
        "code": "code",
        "redirect_uri": redirect_uri,
        "client_id": CLIENT_ID,
        "state": "state",
    }
    if with_pkce:
        expected_token_request_body["code_verifier"] = "code_verifier"
    if with_client_secret:
        expected_token_request_body["client_secret"] = CLIENT_SECRET

    if with_pkce:
        mocker.patch(
            "dash_auth_external.routes.make_code_challenge",
            return_value=("code_challenge", "code_verifier"),
        )

    with app.test_client() as client:
        response = client.get(auth.auth_suffix)
        assert response.status_code == 302

        if with_pkce:
            session_mock.authorization_url.assert_called_with(
                EXTERNAL_AUTH_URL,
                code_challenge="code_challenge",
                code_challenge_method="S256",
            )
        else:
            session_mock.authorization_url.assert_called_with(EXTERNAL_AUTH_URL)

        response = client.get(
            auth.redirect_suffix, query_string={"code": "code", "state": "state"}
        )
        token_request_mock.assert_called_with(
            url=EXERNAL_TOKEN_URL,
            body=expected_token_request_body,
            headers={},
        )

        assert response.status_code == 302
        with client.session_transaction() as session:
            token_data = session[FLASK_SESSION_TOKEN_KEY]
            assert token_data["access_token"] == "access_token"
            assert token_data["refresh_token"] == "refresh_token"
            assert token_data["token_type"] == "Bearer"
            assert token_data["expires_in"] == "3599"
