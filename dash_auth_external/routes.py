from flask import session, redirect, request
import os
import base64
import re
import urllib.parse
from flask.app import Flask
import requests
import hashlib
from requests_oauthlib import OAuth2Session

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


def make_code_challenge(length: int = 40):
    code_verifier = base64.urlsafe_b64encode(os.urandom(length)).decode("utf-8")
    code_verifier = re.sub("[^a-zA-Z0-9]+", "", code_verifier)
    code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).decode("utf-8")
    code_challenge = code_challenge.replace("=", "")
    return code_challenge, code_verifier


def make_auth_route(
    app: Flask,
    external_auth_url: str,
    client_id: str,
    auth_suffix: str,
    redirect_uri: str,
    with_pkce: bool = True,
    client_secret: str = None,
    scope: str = None,
    auth_request_headers: dict = None,
):
    @app.route(auth_suffix)
    def get_auth_code():
        """
        Redirect the user/resource owner to the OAuth provider
        using an URL with a few key OAuth parameters.
        """
        # making code verifier and challenge for PKCE

        if with_pkce:
            code_challenge, code_verifier = make_code_challenge()
            session["cv"] = code_verifier

        # TODO implement this myself
        oauth_session = OAuth2Session(
            client_id,
            redirect_uri=redirect_uri,
            scope=scope,
        )
        authorization_url, state = oauth_session.authorization_url(
            external_auth_url,
            code_challenge=code_challenge,
            code_challenge_method="S256",
        )
        # State is used to prevent CSRF, keep this for later.
        session["oauth_state"] = state

        resp = redirect(authorization_url)
        return resp

    return app


def make_access_token_route(
    app: Flask,
    external_token_url: str,
    client_id: str,
    redirect_suffix: str,
    _home_suffix: str,
    redirect_uri: str,
    with_pkce: bool = True,
    token_request_headers: dict = None,
    client_secret: str = None,
    _token_cookie: str = "token",
    _token_field_name: str = "access_token",
):
    @app.route(redirect_suffix, methods=["GET", "POST"])
    def get_token():

        query = urllib.parse.urlparse(request.url).query
        redirect_params = urllib.parse.parse_qs(query)
        code = redirect_params["code"][0]
        state = redirect_params["state"][0]
        code_verifier = session["cv"]

        headers = token_request_headers

        body = dict(
            grant_type="authorization_code",
            code=code,
            redirect_uri=redirect_uri,
            code_verifier=code_verifier,
            client_id=client_id,
            state=state,
            client_secret=client_secret,
        )

        r = requests.post(external_token_url, data=body, headers=headers)
        if r.status_code != 200:
            raise requests.RequestException(
                f"{r.status_code} {r.reason}:The request to the access token endpoint failed."
            )

        response = redirect(_home_suffix)
        token = r.json()[_token_field_name]
        response.set_cookie(key=_token_cookie, value=token)

        return response

    return app
