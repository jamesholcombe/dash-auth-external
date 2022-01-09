import requests
from dash_auth_external import DashAuthExternal
import pytest
from unittest.mock import Mock, patch
import unittest
from flask import request
from tests.test_config import *

"""Module for integation tests
"""


##this is the least intuitive thing in the world. Patches have to be opposite way round you would expect.
@patch("dash_auth_external.routes.build_token_body")
@patch("dash_auth_external.routes.get_token_response_data")
def test_get_token(mock_post, mock_body):
    auth = DashAuthExternal(EXTERNAL_AUTH_URL,EXERNAL_TOKEN_URL,CLIENT_ID)
    app = auth.server
    
    mock_post.return_value = {auth._token_field_name : "ey.asdfasdfasfd"}
    mock_body.return_value = dict()
    #mocking the two helper functions called within the view function for the redirect to home suffix.

    with app.test_client() as client:
        response = client.get(auth.redirect_suffix)
        assert response.status_code == 302
        mock_post.assert_called_once()
        mock_body.assert_called_once()

        assert auth._token_field_name in response.headers 
        
        
        

        
        
        

     
        
        











        










