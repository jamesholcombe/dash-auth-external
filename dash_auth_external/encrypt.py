from cryptography.fernet import Fernet
import os
from flask import session

class TokenCrypt:

    def encrypt_token(token):
        """The interface for encrypting access tokens from 3rd party OAuth2 Providers.

        Args:
            token (str): The token provided by the OAuth2 Provider. 
        Returns:
           DashAuthExternal: Encrypted token
        """
        if(os.environ.get('pkey') is None or os.environ.get('pkey') == ''):
            key =  Fernet.generate_key()
            os.environ['pkey'] = key.decode()

        key = os.environ['pkey'].encode()
        token = str(token).encode()
        token = Fernet(key).encrypt(token)
        return token


    def decrypt_token(_token_field_name = 'access_token'):
        """The interface for decrypting access tokens from 3rd party OAuth2 Providers.

        Args:
            _token_field_name (str): The key for the token returned in JSON from the token endpoint. Defaults to "access_token".

        Returns:
           DashAuthExternal: Decrypted token
        """
        token = session['token_data'][_token_field_name]
        key = os.environ['pkey']
        token = Fernet(key).decrypt(token)
        token = token.decode()
        return token