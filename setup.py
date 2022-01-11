from setuptools import setup, find_packages
from pathlib import Path

REQUIRES = ["requests", "requests_oauthlib", "flask"]

NAME = "dash-auth-external"

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name=NAME,
    version="0.2.3",
    description="Integrate Dash with 3rd Parties and external providers",
    author_email="jholcombe@hotmail.co.uk",
    url="https://github.com/jamesholcombe/dash-auth-external",
    keywords=["Dash", "Plotly", "Authentication", "Auth", "External"],
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description=long_description,
)
