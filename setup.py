from setuptools import setup, find_packages
from pathlib import Path


NAME = "dash-auth-external"

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()
requires = [
"dash >= 2.0.0",
"requests >= 1.0.0",
"requests-oauthlib >= 0.3.0
]

setup(
    name=NAME,
    version="0.2.4",
    description="Integrate Dash with 3rd Parties and external providers",
    author_email="jholcombe@hotmail.co.uk",
    url="https://github.com/jamesholcombe/dash-auth-external",
    keywords=["Dash", "Plotly", "Authentication", "Auth", "External"],
    install_requires=requires,
    packages=find_packages(),
    include_package_data=True,
    long_description=long_description,
)
