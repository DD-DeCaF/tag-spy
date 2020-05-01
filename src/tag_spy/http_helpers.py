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


"""Provide helpers that interact with a Docker registry."""

import gzip
import json
import logging
from typing import Optional, Union
from urllib.request import (
    HTTPBasicAuthHandler,
    HTTPPasswordMgrWithDefaultRealm,
    OpenerDirector,
    Request,
    build_opener,
)


logger = logging.getLogger(__name__)


def build_authentication_opener(
    registry_url: str, username: Optional[str] = None, password: Optional[str] = None,
) -> OpenerDirector:
    """
    Return an opener director that knows how to authenticate with the registry.

    Args:
        registry_url (str): The URL of the container registry API.
        username (str, optional): A username used for authentication when
            retrieving an access token. Without a username no authentication will be
            attempted.
        password (str, optional): A password used for authentication when
            retrieving an access token. The password field may itself be a token for
            Bearer authentication when the username is 'oauth2accesstoken'.

    Returns:
        OpenerDirector: A director for making HTTP requests. It's main method is `open`.

    """
    opener = build_opener()
    opener.addheaders.extend(
        [
            ("Accept", "application/vnd.docker.distribution.manifest.v2+json"),
            ("Accept-Encoding", "gzip, deflate"),
        ]
    )
    if username is not None:
        assert password is not None, "Authentication requires a password or token."
        # The standard library urllib.request has no HTTPBearerAuthHandler, thus we
        # create a corresponding header ourselves.
        if username.lower() == "oauth2accesstoken":
            opener.addheaders.append(("Authorization", f"Bearer {password}"))
        else:
            password_manager = HTTPPasswordMgrWithDefaultRealm()
            password_manager.add_password(
                None,  # type: ignore
                registry_url,
                username,
                password,
            )
            opener.add_handler(HTTPBasicAuthHandler(password_manager))
    return opener


def build_authenticated_opener(token: str,) -> OpenerDirector:
    """
    Return an opener director that authenticates requests with a Bearer token.

    Args:
        token (str): The access token.

    Returns:
        OpenerDirector: A director for making HTTP requests. It's main method is `open`.

    """
    opener = build_opener()
    opener.addheaders.extend(
        [
            ("Authorization", f"Bearer {token}"),
            ("Accept", "application/vnd.docker.distribution.manifest.v2+json"),
            ("Accept-Encoding", "gzip, deflate"),
        ]
    )
    return opener


def get_response_json(opener: OpenerDirector, url: Union[str, Request]) -> dict:
    """
    Perform an HTTP request and return the body deserialized as JSON.

    Args:
        opener (OpenerDirector): The director that executes the request.
        url (str or urllib.request.Request): The URL to open.

    Returns:
        dict: The JSON body as a dict object.

    Raises:
        urllib.error.HTTPError: In case there is a problem in HTTP communication.
        json.JSONDecodeError: In case the response body can not be deserialized.

    """
    with opener.open(url) as response:
        logger.debug("%d %s", response.status, response.reason)
        logger.debug("%r", response.getheaders())
        content = response.read()
        if response.getheader("Content-Encoding", "").lower() == "gzip":
            content = gzip.decompress(content)
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        logger.debug(content)
        raise
    return dict(data)
