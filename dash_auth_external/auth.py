from dataclasses import asdict
from flask import Flask
from .routes import make_access_token_route, make_auth_route, token_request
from urllib.parse import urljoin
import os
from dash_auth_external.token import OAuth2Token
from dash_auth_external.config import FLASK_SESSION_TOKEN_KEY
from dash_auth_external.exceptions import TokenExpiredError

from flask import session


def generate_secret_key(length: int = 24) -> str:
    """Generates a secret key for flask app.

    Returns:
        bytes: Random bytes of the desired length.
    """
    return os.urandom(length)


def _get_token_data_from_session() -> dict:
    """Gets the token data from the session.

    Returns:
        dict: The token data from the session.
    """
    token_data = session.get(FLASK_SESSION_TOKEN_KEY)
    if token_data is None:
        raise ValueError("No token found in request session.")
    return token_data


def _set_token_data_in_session(token: OAuth2Token):
    session[FLASK_SESSION_TOKEN_KEY] = token


class DashAuthExternal:
    def __init__(
        self,
        external_auth_url: str,
        external_token_url: str,
        client_id: str,
        client_secret: str = None,
        with_pkce=True,
        app_url: str = "http://127.0.0.1:8050",
        redirect_suffix: str = "/redirect",
        auth_suffix: str = "/",
        home_suffix="/home",
        _flask_server: Flask = None,
        _secret_key: str = None,
        auth_request_headers: dict = None,
        token_request_headers: dict = None,
        scope: str = None,
        _server_name: str = __name__,
    ):
        """The interface for obtaining access tokens from 3rd party OAuth2 Providers.

        Args:
            external_auth_url (str): The authorization endpoint for the OAuth2 Provider.
            external_token_url (str): The access token endpoint for the OAuth2 Provider.
            client_id (str): Client ID obtained from OAuth2 provider.
            with_pkce (bool, optional): Use Proof of Key Exchange, reccomended. Enforced by many OAuth2 providers. Defaults to True.
            app_url (str, optional): The url for your dash application Defaults to "http://127.0.0.1:8050".
            redirect_suffix (str, optional): The route that OAuth2 provider will redirect back to. Defaults to "/redirect".
            auth_suffix (str, optional): The route that will trigger the initial redirect to the external OAuth provider. Defaults to "/".
            home_suffix (str, optional): The route your dash application will sit, relative to your url. Defaults to "/home".
            _flask_server (Flask, optional): Flask server to use if additional config required. Defaults to None.
            _secret_key (str, optional): Secret key for flask app, normally generated at runtime. Defaults to None.
            auth_request_headers (dict, optional): Additional headers to send to the authorization endpoint. Defaults to None.
            token_request_headers (dict, optional): Additional headers to send to the access token endpoint. Defaults to None.
            scope (str, optional): Header required by most Oauth2 Providers. Defaults to None.
            _server_name (str, optional): The name of the Flask Server. Defaults to __name__, ignored if _flask_server is not None.


        Returns:
           DashAuthExternal: Main package class
        """

        if auth_request_headers is None:
            auth_request_headers = {}
        if token_request_headers is None:
            token_request_headers = {}

        if _flask_server is None:
            app = Flask(
                _server_name, instance_relative_config=False, static_folder="./assets"
            )
        else:
            app = _flask_server

        if _secret_key is None:
            app.secret_key = generate_secret_key()
        else:
            app.secret_key = _secret_key

        redirect_uri = urljoin(app_url, redirect_suffix)

        app = make_auth_route(
            app=app,
            external_auth_url=external_auth_url,
            client_id=client_id,
            auth_suffix=auth_suffix,
            redirect_uri=redirect_uri,
            with_pkce=with_pkce,
            scope=scope,
            auth_request_params=auth_request_headers,
        )
        app = make_access_token_route(
            app,
            external_token_url=external_token_url,
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            redirect_suffix=redirect_suffix,
            _home_suffix=home_suffix,
            token_request_headers=token_request_headers,
            with_pkce=with_pkce,
        )

        self.server = app
        self.home_suffix = home_suffix
        self.redirect_suffix = redirect_suffix
        self.auth_suffix = auth_suffix
        self.client_id = client_id
        self.external_token_url = external_token_url
        self.token_request_headers = token_request_headers
        self.scope = scope

    def get_token_data(self) -> OAuth2Token:
        """Attempts to get a valid access token.

        Returns:
            OAuth2Token: The token data.
        """
        token_data = _get_token_data_from_session()

        token = OAuth2Token(**token_data)

        if not token.is_expired():
            return token

        if not token.refresh_token:
            raise TokenExpiredError(
                "Token is expired and no refresh token available to refresh token."
            )

        token_data = refresh_token(
            self.external_token_url, token_data, self.token_request_headers
        )
        _set_token_data_in_session(token_data)
        return token_data

    def get_token(self) -> str:
        """Attempts to get a valid access token.

        Returns:
            str: The access token.
        """
        return self.get_token_data().access_token


def refresh_token(url: str, token_data: OAuth2Token, headers: dict) -> OAuth2Token:
    body = {
        "grant_type": "refresh_token",
        "refresh_token": token_data.refresh_token,
    }
    data = token_request(url, body, headers)

    new_token = OAuth2Token(
        access_token=data["access_token"],
        token_type=data.get("token_type"),
        expires_in=data.get("expires_in"),
        refresh_token=data.get("refresh_token"),
        token_data=data,
    )

    return new_token
