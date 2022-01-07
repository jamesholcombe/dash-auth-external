from flask import Flask
import flask
from werkzeug.routing import RoutingException, ValidationError
from .routes import make_access_token_route, make_auth_route
from urllib.parse import urljoin
import os


class DashAuthExternal:
    @staticmethod
    def generate_secret_key(length: int = 24):
        """Generates a secret key for flask app.

        Returns:
            bytes: Random bytes of the desired length.
        """
        return os.urandom(length)

    def get_token(self):
        """Retrieves the access token from flask request headers, using the token cookie given on __init__.

        Returns:
            str: Bearer Access token from your OAuth2 Provider
        """

        try:
            return flask.request.cookies.get(self._token_cookie)
        except RuntimeError:
            raise ValueError(
                "This method must be called in a callback as it makes use of the flask request context."
            )

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
        _token_cookie: str = "token",
        client_secret: str = None,
        _secret_key: str = None,
        auth_request_headers: dict = None,
        token_request_headers: dict = None,
        scope: str = None,
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
            _token_cookie (str, optional): The name to save your access token in the flask request cookies. Defaults to "token".
            client_secret (str, optional): Client secret if enforced by Oauth2 provider. Defaults to None.
            _secret_key (str, optional): Secret key for flask app, normally generated at runtime. Defaults to None.
            auth_request_headers (dict, optional): Additional headers to send to the authorization endpoint. Defaults to None.
            token_request_headers (dict, optional): Additional headers to send to the access token endpoint. Defaults to None.
            scope (str, optional): Header required by most Oauth2 Providers. Defaults to None.

        Returns:
           DashAuthExternal: Main package class
        """
        app = Flask(__name__, instance_relative_config=False)

        self._token_cookie = _token_cookie

        if _secret_key is None:
            app.secret_key = self.generate_secret_key()
        else:
            app.secret_key = _secret_key

        redirect_uri = urljoin(app_url, redirect_suffix)

        app = make_auth_route(
            app=app,
            external_auth_url=external_auth_url,
            client_id=client_id,
            client_secret=client_secret,
            auth_suffix=auth_suffix,
            redirect_uri=redirect_uri,
            with_pkce=with_pkce,
            scope=scope,
            auth_request_headers=auth_request_headers,
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
        )

        self.server = app
