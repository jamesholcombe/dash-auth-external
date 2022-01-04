from setuptools import setup, find_packages

REQUIRES = ["requests", "requests_oauthlib", "flask"]

NAME = "dash-auth-external"

setup(
    name=NAME,
    version="0.1",
    description="Integrate Dash with 3rd Parties and external providers",
    author_email="jholcombe@hotmail.co.uk",
    url="",
    keywords=["Dash", "Plotly", "Authentication", "Auth", "External"],
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description="""\
    Integrate Dash with 3rd Parties and external providers"
    """,
)
