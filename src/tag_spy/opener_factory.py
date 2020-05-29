# Copyright 2020 Novo Nordisk Foundation Center for Biosustainability,
# Technical University of Denmark.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Provide factory functions for creating opener directors."""


from typing import List, Tuple
from urllib.request import (
    HTTPBasicAuthHandler,
    HTTPPasswordMgrWithDefaultRealm,
    OpenerDirector,
    build_opener,
)


def generate_standard_headers() -> List[Tuple[str, str]]:
    """Generate a standard list of HTTP header, value pairs for openers."""
    return [
        ("Accept", "application/vnd.docker.distribution.manifest.v2+json"),
        ("Accept-Encoding", "gzip, deflate"),
    ]


def opener_factory() -> OpenerDirector:
    """Return a basic opener director with standard headers."""
    opener = build_opener()
    opener.addheaders.extend(generate_standard_headers())
    return opener


def basic_authentication_opener_factory(
    registry_url: str, username: str, password: str,
) -> OpenerDirector:
    """
    Return an opener director that authenticates requests using the Basic scheme.

    Args:
        registry_url (str): The URL of the container registry API.
        username (str): A username used for Basic authentication when retrieving an
            access token.
        password (str): A password used for Basic authentication when
            retrieving an access token.

    Returns:
        OpenerDirector: A director for making HTTP requests. It's main method is `open`.

    """
    opener = opener_factory()
    password_manager = HTTPPasswordMgrWithDefaultRealm()
    password_manager.add_password(
        None,  # type: ignore
        registry_url,
        username,
        password,
    )
    opener.add_handler(HTTPBasicAuthHandler(password_manager))
    return opener
