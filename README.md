# dash-auth-external

 Integrate your dashboards with 3rd parties and external OAuth providers. 

## Overview

Do you want to build a Plotly Dash app which pulls user data from Google, Spotify, Slack etc?

**Dash-auth-external** provides a simple interface to authenticate users through OAuth2 code flow. Allowing developers to serve user tailored content. 

## Installation
**Dash-auth-external** is distributed via [PyPi](https://pypi.org/project/dash-auth-external/)

``` 
pip install dash-auth-external
```
## Simple Usage
```
#using spotify as an example
AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
CLIENT_ID = "YOUR_CLIENT_ID"

# creating the instance of our auth class
auth = DashAuthExternal(AUTH_URL, TOKEN_URL, CLIENT_ID)
```
We then pass the flask server from this object to dash on init.
```
app = Dash(__name__, server= auth.server)
```
That's it! You can now define your layout and callbacks as usual. 
> To obtain your access token, call the get_token method of your Auth object.
> **NOTE** This can **ONLY** be done in the context of a dash callback.
```

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









