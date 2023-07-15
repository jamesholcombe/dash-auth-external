from setuptools import setup, find_packages
from pathlib import Path


NAME = "dash-auth-external"

this_directory = Path(__file__).parent
description = (
    "Integrate your dashboards with 3rd party APIs and external OAuth providers."
)

with open(this_directory / "README.md", encoding="utf-8") as f:
    long_description = f.read()



requires = ["dash >= 2.0.0", "requests >= 1.0.0", "requests-oauthlib >= 0.3.0"]

setup(
    name=NAME,
    version="1.2.0",
    description=description,
    python_requires=">=3.7",
    author_email="jholcombe@hotmail.co.uk",
    url="https://github.com/jamesholcombe/dash-auth-external",
    keywords=["Dash", "Plotly", "Authentication", "Auth", "External"],
    install_requires=requires,
    packages=find_packages(),
    include_package_data=True,
    long_description=long_description,
)
