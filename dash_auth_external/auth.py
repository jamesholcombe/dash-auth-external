from flask import Flask
import flask
from werkzeug.routing import RoutingException, ValidationError
from .routes import make_access_token_route, make_auth_route, refresh_token
from urllib.parse import urljoin
import os
from dash_auth_external.token import OAuth2Token
from dash_auth_external.config import FLASK_HEADER_TOKEN_KEY
from dash_auth_external.exceptions import TokenExpiredError
import json


class DashAuthExternal:
    @staticmethod
    def generate_secret_key(length: int = 24) -> str:
        """Generates a secret key for flask app.

        Returns:
            bytes: Random bytes of the desired length.
        """
        return os.urandom(length)

    def get_token(self) -> str:
        """Attempts to get a valid access token.

        Returns:
            str: Bearer Access token from your OAuth2 Provider
        """

        if self.token_data is not None:
            if not self.token_data.is_expired():
                return self.token_data.access_token

            if not self.token_data.refresh_token:
                raise TokenExpiredError(
                    "Token is expired and no refresh token available to refresh token."
                )

            self.token_data = refresh_token(
                self.external_token_url, self.token_data, self.token_request_headers
            )
            return self.token_data.access_token

        token_data = flask.request.headers.get(FLASK_HEADER_TOKEN_KEY)
        token_data = json.loads(token_data)
        if token_data is None:
            raise ValueError("No token found in request headers.")
        self.token_data = OAuth2Token(
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            expires_in=token_data.get("expires_in"),
            token_type=token_data.get("token_type"),
        )

        return self.token_data.access_token

    def __init__(
        self,
        external_auth_url: str,
        external_token_url: str,
        client_id: str,
        with_pkce=True,
        app_url: str = "http://127.0.0.1:8050",
        redirect_suffix: str = "/redirect",
        auth_suffix: str = "/",
        home_suffix="/home",
        _token_field_name: str = "access_token",
        _secret_key: str = None,
        auth_request_headers: dict = None,
        token_request_headers: dict = None,
        scope: str = None,
        _server_name: str = __name__,
        _static_folder: str = "./assets/",
        **kwargs: dict,
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
            _token_field_name (str, optional): The key for the token returned in JSON from the token endpoint. Defaults to "access_token".
            _secret_key (str, optional): Secret key for flask app, normally generated at runtime. Defaults to None.
            auth_request_headers (dict, optional): Additional params to send to the authorization endpoint. Defaults to None.
            token_request_headers (dict, optional): Additional headers to send to the access token endpoint. Defaults to None.
            scope (str, optional): Header required by most Oauth2 Providers. Defaults to None.
            _server_name (str, optional): The name of the Flask Server. Defaults to __name__, so the name of this library.
            _static_folder (str, optional): The folder with static assets. Defaults to "./assets/".
            **kwargs: Additional keyword arguments to pass to the Flask server. See Flask documentation for more information.

        Returns:
           DashAuthExternal: Main package class
        """

        self.token_data: OAuth2Token = None

        app = Flask(
            _server_name,
            instance_relative_config=False,
            static_folder=_static_folder,
            **kwargs,
        )

        if _secret_key is None:
            app.secret_key = self.generate_secret_key()
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
            redirect_uri=redirect_uri,
            redirect_suffix=redirect_suffix,
            _home_suffix=home_suffix,
            token_request_headers=token_request_headers,
            _token_field_name=_token_field_name,
            with_pkce=with_pkce,
        )

        self.server = app
        self.home_suffix = home_suffix
        self.redirect_suffix = redirect_suffix
        self.auth_suffix = auth_suffix
        self._token_field_name = _token_field_name
        self.client_id = client_id
        self.external_token_url = external_token_url
        self.token_request_headers = token_request_headers
