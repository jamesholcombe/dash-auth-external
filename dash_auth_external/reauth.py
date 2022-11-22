from flask.json import jsonify
from requests_oauthlib import OAuth2Session
from flask import session
from time import time
from .encrypt import *

class RefreshAuth:
    def __init__(
            self,
            external_token_url: str,
            keycloack_userinfo_url: str,
            client_id: str,
            client_secret: str = None,
            _token_field_name: str = "access_token",
            
        ):
            """The interface for obtaining access tokens from 3rd party OAuth2 Providers.

            Args:
                external_token_url (str): The access token endpoint for the OAuth2 Provider.
                keycloack_userinfo_url (str): The userinfo endpoint for the OAuth2 Provider.
                client_id (str): Client ID obtained from OAuth2 provider.
                client_secret (str, optional): Client secret if enforced by Oauth2 provider. Defaults to None.
                _token_field_name (str, optional): The key for the token returned in JSON from the token endpoint. Defaults to "access_token".

            Returns:
            DashAuthExternal: reauth.py (new token generated)
            """

            
            """Refreshing an OAuth 2 token using a refresh token."""

            token = TokenCrypt.decrypt_token(_token_field_name)
            token_data =  session['token_data']
            token_data[_token_field_name] = token

            refresh_url = external_token_url

            # We force an expiration by setting expired at in the past.
            # This will trigger an automatic refresh next time we interact with
            # API.
            token_data['expires_at'] = time() - 10

            extra = {
                'client_id': client_id,
                'client_secret': client_secret,
            }

            def token_updater(token_data):
                token_data[_token_field_name] = TokenCrypt.encrypt_token(token_data[_token_field_name])
                session['token_data'] = token_data

            api = OAuth2Session(client_id,
                                token=token_data,
                                auto_refresh_kwargs=extra,
                                auto_refresh_url=refresh_url,
                                token_updater=token_updater)


            # Trigger the automatic refresh
            jsonify(api.get(keycloack_userinfo_url).json())
            self._token_field_name = _token_field_name

            return


