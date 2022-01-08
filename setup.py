from setuptools import setup, find_packages

REQUIRES = ["requests", "requests_oauthlib", "flask"]

NAME = "dash-auth-external"

setup(
    name=NAME,
    version="0.2.1",
    description="Integrate Dash with 3rd Parties and external providers",
    author_email="jholcombe@hotmail.co.uk",
    url="https://github.com/jamesholcombe/dash-auth-external",
    keywords=["Dash", "Plotly", "Authentication", "Auth", "External"],
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description="""\
    Integrate Plotly Dash with 3rd Parties and external providers."
    """,
)
