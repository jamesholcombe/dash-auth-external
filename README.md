# dash-auth-external

Integrate your dashboards with 3rd party APIs and external OAuth providers.

## Overview

Do you want to build a Plotly Dash app which pulls user data from external APIs such as Google, Spotify, Slack etc?

**Dash-auth-external** provides a simple interface to authenticate users through OAuth2 code flow. Allowing developers to serve user tailored content.

## Installation

**Dash-auth-external** is distributed via [PyPi](https://pypi.org/project/dash-auth-external/)

```
pip install dash-auth-external
```

## Simple Usage

```python
#using spotify as an example
AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
CLIENT_ID = "YOUR_CLIENT_ID"

# creating the instance of our auth class
auth = DashAuthExternal(AUTH_URL, TOKEN_URL, CLIENT_ID)
```

We then pass the flask server from this object to dash on init.

```python
app = Dash(__name__, server= auth.server)
```

That's it! You can now define your layout and callbacks as usual.

> To obtain your access token, call the get_token method of your Auth object.
> **NOTE** This can **ONLY** be done in the context of a dash callback.

```python
app.layout = html.Div(
[
html.Div(id="example-output"),
dcc.Input(id="example-input")
])

@app.callback(
Output("example-output", "children"),
Input("example-input", "value")
)
def example_callback(value):
    token = (
        auth.get_token()
    )  ##The token can only be retrieved in the context of a dash callback
    return token
```

## Troubleshooting

If you hit 400 responses (bad request) from either endpoint, there are a number of things that might need configuration.

Make sure you have checked the following

- **Register your redirect URI** with OAuth provider!

_The library uses a default redirect URI of http://127.0.0.1:8050/redirect_.

- Check the **key field** for the **token** in the JSON response returned by the token endpoint by your OAuth provider.

_The default is "access_token" but different OAuth providers may use a different key for this._



## Reauth method
To use the token refresh method import reauth.py into your project and call the RefreshAuth class with the necessary parameters when you want to refresh the token. If you are using the token encryption methods be sure to encrypt and decrypt tokens where required. 


## Encrypted Token Usage

The token will be stored in the HTTP header. The token is encrypted using Fernet symmetric encryption.
You can find out more about Fernet here: https://cryptography.io/en/latest/fernet/.
The token is stored in the header as an encrypted key. The encryption method uses a private key which is generated on the first execution of the method. 
To use the stored token decrypt the token using the private key stored in the enviorment variable "pkey".

## Contributing

Contributions, issues, and ideas are all more than welcome
