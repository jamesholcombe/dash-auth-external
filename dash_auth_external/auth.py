import dash
from flask import Flask
import flask
from .routes import make_routes


def generate_secret_key():
    pass


class DashAuthExternal:

    def get_token(self):
        return flask.request.cookies.get(self._token_cookie)
    

    def __init__(
        self,
        external_auth_url: str,
        external_token_url: str,
        client_id: str,
        app_url: str = "http://127.0.0.1:8050",
        client_secret: str = None,
        redirect_suffix: str = "/redirect",
        auth_suffix: str = "/auth",
        _token_cookie: str = "token",
        _secret_key: str = None,
        home_suffix="/",
        scope: str = None,
    ):
        app = Flask(__name__, instance_relative_config=False)
        
        self._token_cookie = _token_cookie
        
        if _secret_key is None:
            app.secret_key = generate_secret_key()
        else:
            app.secret_key = _secret_key

        redirect_uri = app_url + redirect_suffix

        app = make_routes(
            app=app,
            external_auth_url=external_auth_url,
            external_token_url=external_token_url,
            client_id=client_id,
            client_secret=client_secret,
            redirect_suffix=redirect_suffix,
            redirect_uri=redirect_uri,
            auth_suffix=auth_suffix,
            scope=scope,
            _token_cookie=_token_cookie,
        )

        return app
