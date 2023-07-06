from dataclasses import asdict
from flask import session, redirect, request
import os
import base64
import re
import urllib.parse
from flask.app import Flask
import requests
import hashlib
from requests_oauthlib import OAuth2Session
from dash_auth_external.config import FLASK_SESSION_TOKEN_KEY
from dash_auth_external.token import OAuth2Token

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
    with_pkce: bool,
    scope: str,
    auth_request_params: dict,
):
    @app.route(auth_suffix)
    def get_auth_code():
        """
        Redirect the user/resource owner to the OAuth provider
        using an URL with a few key OAuth parameters.
        """
        oauth_session = OAuth2Session(
            client_id,
            redirect_uri=redirect_uri,
            scope=scope,
        )

        if with_pkce:
            code_challenge, code_verifier = make_code_challenge()
            session["cv"] = code_verifier
            authorization_url, state = oauth_session.authorization_url(
                external_auth_url,
                code_challenge=code_challenge,
                code_challenge_method="S256",
                **auth_request_params,
            )
        else:
            authorization_url, state = oauth_session.authorization_url(
                external_auth_url,
                **auth_request_params,
            )

        resp = redirect(authorization_url)
        return resp

    return app


def build_token_body(
    url: str, redirect_uri: str, client_id: str, with_pkce: bool, client_secret: str
):
    query = urllib.parse.urlparse(url).query
    redirect_params = urllib.parse.parse_qs(query)
    code = redirect_params["code"][0]
    state = redirect_params["state"][0]
    body = dict(
        grant_type="authorization_code",
        code=code,
        redirect_uri=redirect_uri,
        client_id=client_id,
        state=state,
    )

    if with_pkce:
        body["code_verifier"] = session["cv"]

    if client_secret:
        body["client_secret"] = client_secret

    return body


def make_access_token_route(
    app: Flask,
    external_token_url: str,
    redirect_suffix: str,
    _home_suffix: str,
    redirect_uri: str,
    client_id: str,
    client_secret: str,
    with_pkce: bool,
    token_request_headers: dict,
):
    @app.route(redirect_suffix, methods=["GET", "POST"])
    def get_token_route():
        url = request.url
        body = build_token_body(
            url=url,
            redirect_uri=redirect_uri,
            with_pkce=with_pkce,
            client_id=client_id,
            client_secret=client_secret,
        )

        response_data = token_request(
            url=external_token_url,
            body=body,
            headers=token_request_headers,
        )

        response = redirect(_home_suffix)

        session[FLASK_SESSION_TOKEN_KEY] = asdict(OAuth2Token(**response_data))

        return response

    return app


def token_request(url: str, body: dict, headers: dict):
    r = requests.post(url, data=body, headers=headers)
    r.raise_for_status()
    return r.json()
