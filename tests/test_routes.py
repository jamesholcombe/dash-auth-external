from .test_context import dash_auth_external
from unittest import mock
import pytest
import requests
from werkzeug.wrappers import request
from dash_auth_external.auth import DashAuthExternal
from dash_auth_external.routes import token_request
import flask

"""Module for unit tests
"""


@mock.patch("dash_auth_external.routes.requests.post")
def test_token_route_ok(mock_post):

    mock_post.return_value.status_code = 200
    response = token_request("Fakeurl", dict(), dict())
    assert response.status_code == 200


@mock.patch("dash_auth_external.routes.requests.post")
def test_token_route_raises(mock_post):
    mock_post.return_value.status_code = 400

    with pytest.raises(requests.RequestException):
        response = token_request("Fakeurl", dict(), dict())


def test_auth_route_ok():
    pass


def test_auth_route_raises():
    pass


def test_make_token_body():
    pass
