from dash_auth_external import DashAuthExternal
from unittest.mock import Mock
from dash_auth_external.config import FLASK_HEADER_TOKEN_KEY
from dash_auth_external.exceptions import TokenExpiredError
from dash_auth_external.token import OAuth2Token
from .test_config import EXERNAL_TOKEN_URL, EXTERNAL_AUTH_URL, CLIENT_ID
from pytest_mock import mocker
from requests_oauthlib import OAuth2Session
from dash import Dash, Input, Output, html, dcc
import pytest


@pytest.fixture()
def dash_app_and_auth():
    auth = DashAuthExternal(EXTERNAL_AUTH_URL, EXERNAL_TOKEN_URL, CLIENT_ID)

    app = Dash(__name__, server=auth.server)

    app.layout = html.Div([html.Div(id="test-output"), dcc.Input(id="test-input")])
    return app, auth


@pytest.fixture()
def access_token_data_with_refresh():
    return {
        "access_token": "access_token",
        "refresh_token": "refresh_token",
        "token_type": "Bearer",
        "expires_in": 3599,
    }


@pytest.fixture()
def expired_access_token_data_without_refresh():
    return {
        "access_token": "access_token",
        "token_type": "Bearer",
        "expires_in": -1,
    }


@pytest.fixture()
def expired_access_token_data_with_refresh(expired_access_token_data_without_refresh):
    return {
        **expired_access_token_data_without_refresh,
        "refresh_token": "refresh_token",
    }


def test_get_token_first_call(
    dash_app_and_auth, mocker, access_token_data_with_refresh
):
    dash_app, auth = dash_app_and_auth

    mocker.patch(
        "dash_auth_external.auth._get_token_data_from_session",
        return_value=access_token_data_with_refresh,
    )

    @dash_app.callback(Output("test-output", "children"), Input("test-input", "value"))
    def test_callback(value):
        token = auth.get_token()
        return token

    assert auth.token_data is None
    test_callback("test")
    assert isinstance(auth.token_data, OAuth2Token)


def test_get_token_second_call(
    dash_app_and_auth, mocker, access_token_data_with_refresh
):
    dash_app, auth = dash_app_and_auth

    mocker.patch(
        "dash_auth_external.auth._get_token_data_from_session",
        return_value=access_token_data_with_refresh,
    )

    @dash_app.callback(Output("test-output", "children"), Input("test-input", "value"))
    def test_callback(value):
        token = auth.get_token()
        return token

    assert auth.token_data is None
    test_callback("test")
    assert isinstance(auth.token_data, OAuth2Token)
    test_callback("test")
    assert isinstance(auth.token_data, OAuth2Token)


def test_get_token_with_refresh(
    dash_app_and_auth,
    mocker,
    expired_access_token_data_with_refresh,
    access_token_data_with_refresh,
):
    dash_app, auth = dash_app_and_auth

    refresh_mock = mocker.patch(
        "dash_auth_external.auth.refresh_token",
        return_value=OAuth2Token(**access_token_data_with_refresh),
    )

    @dash_app.callback(Output("test-output", "children"), Input("test-input", "value"))
    def test_callback(value):
        token = auth.get_token()
        return token

    auth.token_data = OAuth2Token(**expired_access_token_data_with_refresh)

    test_callback("test")
    assert isinstance(auth.token_data, OAuth2Token)
    assert auth.token_data.expires_in > 0
    refresh_mock.assert_called_once()


def test_expired_token_raises_exception(
    dash_app_and_auth, mocker, expired_access_token_data_without_refresh
):
    dash_app, auth = dash_app_and_auth

    mocker.patch(
        "dash_auth_external.auth._get_token_data_from_session",
        return_value=expired_access_token_data_without_refresh,
    )

    @dash_app.callback(Output("test-output", "children"), Input("test-input", "value"))
    def test_callback(value):
        token = auth.get_token()
        return token

    auth.token_data = OAuth2Token(**expired_access_token_data_without_refresh)

    with pytest.raises(TokenExpiredError):
        test_callback("test")
