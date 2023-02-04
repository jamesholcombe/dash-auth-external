"""Module for integation tests, testing full OAuth2 flow, excluding the get_token method
"""

from dash_auth_external import DashAuthExternal
from unittest.mock import Mock
from dash_auth_external.config import FLASK_SESSION_TOKEN_KEY
from .test_config import EXERNAL_TOKEN_URL, EXTERNAL_AUTH_URL, CLIENT_ID
from pytest_mock import mocker
from requests_oauthlib import OAuth2Session


def test_pkce_true(mocker):
    auth = DashAuthExternal(
        EXTERNAL_AUTH_URL, EXERNAL_TOKEN_URL, CLIENT_ID, with_pkce=True
    )
    app = auth.server

    redirect_uri = "http://localhost:8050"
    session_mock = Mock(
        OAuth2Session(CLIENT_ID, redirect_uri=redirect_uri, scope=auth.scope)
    )

    session_mock.authorization_url.return_value = (
        "https://example.com", "state")

    mocker.patch("dash_auth_external.routes.OAuth2Session",
                 return_value=session_mock)

    mocker.patch(
        "dash_auth_external.routes.make_code_challenge",
        return_value=("code_challenge", "code_verifier"),
    )

    # mocking the two helper functions called within the view function for the redirect to home suffix.

    with app.test_client() as client:

        response = client.get(auth.auth_suffix)
        assert response.status_code == 302

        # assert that the authorization_url method was called with the correct arguments
        session_mock.authorization_url.assert_called_with(
            EXTERNAL_AUTH_URL,
            code_challenge="code_challenge",
            code_challenge_method="S256",
        )

        # user logs in and is redirected to the redirect_uri, with a code and state

        # mocking the token request in the token route
        mocker.patch(
            "dash_auth_external.routes.token_request",
            return_value={
                "access_token": "access_token",
                "refresh_token": "refresh_token",
                "token_type": "Bearer",
                "expires_in": "3599",
            },
        )

        # now we call the token route with the code and state returned from the authorization_url method
        response = client.get(
            auth.redirect_suffix, query_string={
                "code": "code", "state": "state"}
        )
        assert response.status_code == 302
        with client.session_transaction() as session:
            token_data = session[FLASK_SESSION_TOKEN_KEY]
            assert token_data["access_token"] == "access_token"
            assert token_data["refresh_token"] == "refresh_token"
            assert token_data["token_type"] == "Bearer"
            assert token_data["expires_in"] == "3599"


def test_pkce_false(mocker):
    auth = DashAuthExternal(
        EXTERNAL_AUTH_URL, EXERNAL_TOKEN_URL, CLIENT_ID, with_pkce=False
    )
    app = auth.server

    redirect_uri = "http://localhost:8050"
    session_mock = Mock(
        OAuth2Session(CLIENT_ID, redirect_uri=redirect_uri, scope=auth.scope)
    )

    session_mock.authorization_url.return_value = (
        "https://example.com", "state")

    mocker.patch("dash_auth_external.routes.OAuth2Session",
                 return_value=session_mock)

    with app.test_client() as client:

        response = client.get(auth.auth_suffix)
        assert response.status_code == 302

        # assert that the authorization_url method was called with the correct arguments
        session_mock.authorization_url.assert_called_with(EXTERNAL_AUTH_URL)

        # user logs in and is redirected to the redirect_uri, with a code and state

        # mocking the token request in the token route
        mocker.patch(
            "dash_auth_external.routes.token_request",
            return_value={
                "access_token": "access_token",
                "refresh_token": "refresh_token",
                "token_type": "Bearer",
                "expires_in": "3599",
            },
        )

        # now we call the token route with the code and state returned from the authorization_url method
        response = client.get(
            auth.redirect_suffix, query_string={
                "code": "code", "state": "state"}
        )
        assert response.status_code == 302
        with client.session_transaction() as session:
            token_data = session[FLASK_SESSION_TOKEN_KEY]
            assert token_data["access_token"] == "access_token"
            assert token_data["refresh_token"] == "refresh_token"
            assert token_data["token_type"] == "Bearer"
            assert token_data["expires_in"] == "3599"
