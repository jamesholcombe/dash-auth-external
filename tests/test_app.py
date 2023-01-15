import requests
from dash_auth_external import DashAuthExternal
import pytest
from unittest.mock import Mock, patch
import unittest
from flask import request
from .test_config import EXERNAL_TOKEN_URL, EXTERNAL_AUTH_URL, CLIENT_ID
from pytest_mock import mocker

"""Module for integation tests
"""


def test_pkce_true(mocker):
    auth = DashAuthExternal(
        EXTERNAL_AUTH_URL, EXERNAL_TOKEN_URL, CLIENT_ID, with_pkce=True)
    app = auth.server

    # mocking the two helper functions called within the view function for the redirect to home suffix.

    with app.test_client() as client:
        response = client.get(auth.redirect_suffix)
        assert response.status_code == 302

        assert auth._token_field_name in response.headers
