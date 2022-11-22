from flask import session, redirect, request
import os
from os import environ
import base64
import re
import urllib.parse
from flask.app import Flask
import flask
import requests
import hashlib
from requests_oauthlib import OAuth2Session
from flask.json import jsonify
from ua_parser import user_agent_parser
from time import time
from .encrypt import *


os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
# Uncomment for detailed oauthlib logs
import logging
import sys
log = logging.getLogger('oauthlib')
log.addHandler(logging.StreamHandler(sys.stdout))
log.setLevel(logging.DEBUG)

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
            scope=scope
        )

        if with_pkce:

            authorization_url, state = oauth_session.authorization_url(
                external_auth_url,
                code_challenge=code_challenge,
                code_challenge_method="S256",
            )
        else:
            authorization_url, state = oauth_session.authorization_url(
                external_auth_url,
            )

        resp = redirect(authorization_url)
        return resp

    return app


def build_token_body(
    url, redirect_uri: str, client_id: str, with_pkce: bool, client_secret: str
):
    query = urllib.parse.urlparse(url).query
    redirect_params = urllib.parse.parse_qs(query)
    code = redirect_params["code"][0]
    state = redirect_params["state"][0]

    if with_pkce:
        code_verifier = session["cv"]
        body = dict(
            grant_type="authorization_code",
            code=code,
            redirect_uri=redirect_uri,
            code_verifier=code_verifier,
            client_id=client_id,
            state=state,
            client_secret=client_secret,
        )
    else:
        body = dict(
            grant_type="authorization_code",
            code=code,
            redirect_uri=redirect_uri,
            client_id=client_id,
            state=state,
            client_secret=client_secret,
        )
    return body


def make_access_token_route(
    app: Flask,
    external_token_url: str,
    redirect_suffix: str,
    _home_suffix: str,
    redirect_uri: str,
    client_id: str,
    _token_field_name: str,
    with_pkce: bool = True,
    client_secret: str = None,
    keycloak_userinfo_url : str = None,
    refresh_suffix: str = None,
    token_request_headers: dict = None,
):
    @app.route(redirect_suffix, methods=["GET", "POST"])
    def get_token():
        url = request.url
        body = build_token_body(
            url=url,
            redirect_uri=redirect_uri,
            with_pkce=with_pkce,
            client_id=client_id,
            client_secret=client_secret,
        )
        body['access_type'] = 'offline'


        response_data = get_token_response_data(
            external_token_url, body, token_request_headers
        )
        token = response_data[_token_field_name]
        token = TokenCrypt.encrypt_token(token)
        response_data[_token_field_name]  = token

        session['token_data'] = response_data

        response = redirect(_home_suffix)
        response.headers.add(_token_field_name, token)

        set_cookie(
            response=response,
            name= _token_field_name,
            value= token,
            max_age=None
        )
        return response
    return app

def set_cookie(response, name, value, max_age,
                   httponly=True, samesite='Strict'):

        is_http = flask.request.environ.get(
            'wsgi.url_scheme',
            flask.request.environ.get('HTTP_X_FORWARDED_PROTO', 'http')
        ) == 'http'

        ua = user_agent_parser.ParseUserAgent(
            flask.request.environ.get('HTTP_USER_AGENT', ''))



        response.set_cookie(
            name,
            value=value,
            max_age=max_age,
            httponly=httponly,
            samesite=samesite
        )


def token_request(url: str, body: dict, headers: dict):
    r = requests.post(url, data=body, headers=headers)

    if r.status_code != 200:
        raise requests.RequestException(
            f"{r.status_code} {r.reason}:The request to the access token endpoint failed."
        )
    return r


def get_token_response_data(*args):
    r = token_request(*args)
    return r.json()
