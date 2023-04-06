from setuptools import setup, find_packages
from pathlib import Path


NAME = "dash-auth-external"

this_directory = Path(__file__).parent
long_description = (
    "Integrate your dashboards with 3rd party APIs and external OAuth providers."
)
requires = ["dash >= 2.0.0", "requests >= 1.0.0", "requests-oauthlib >= 0.3.0"]

setup(
    name=NAME,
    version="1.0.0",
    description="Integrate Dash with 3rd Parties and external providers",
    python_requires=">=3.7",
    author_email="jholcombe@hotmail.co.uk",
    url="https://github.com/jamesholcombe/dash-auth-external",
    keywords=["Dash", "Plotly", "Authentication", "Auth", "External"],
    install_requires=requires,
    packages=find_packages(),
    include_package_data=True,
    long_description=long_description,
)
