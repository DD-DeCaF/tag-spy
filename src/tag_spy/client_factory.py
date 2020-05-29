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


import logging
from typing import Optional
from urllib.parse import urljoin

from .http_client import Client
from .opener_factory import basic_authentication_opener_factory, opener_factory
from .registry_helpers import get_token


logger = logging.getLogger(__name__)


def authenticated_client_factory(
    registry_url: str,
    authentication_url: str,
    image: str,
    service: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
) -> Client:
    """
    Create a client instance which is authenticated with an access token.

    Args:
        registry_url (str): The URL of the container registry API.
        authentication_url (str): The URL from where to retrieve an access
            token for the registry.
        image (str): The fully specified image name, for example, 'dddecaf/wsgi-base'.
        service (str): The service URI for which to request an access token.
        username (str, optional): A username used for authentication when
            retrieving an access token. Without a username no authentication will be
            attempted which will only succeed with public registries.
        password (str, optional): A password used for authentication when
            retrieving an access token. The password field may itself be a token for
            Bearer authentication iff the username is 'oauth2accesstoken'.

    Returns:
        Client: An HTTP client equipped with a Bearer token according to the privileges
            granted by the provided credentials.

    """
    if username is not None:
        assert password is not None, "Authentication requires a password or token."
        if username.lower() == "oauth2accesstoken":
            logger.debug("Retrieving access token using Bearer authentication.")
            token = get_token(
                Client(
                    opener=opener_factory(), base_url=authentication_url, token=password
                ),
                image,
                service,
            )
        else:
            logger.debug("Retrieving access token using Basic authentication.")
            token = get_token(
                Client(
                    opener=basic_authentication_opener_factory(
                        registry_url, username, password
                    ),
                    base_url=authentication_url,
                ),
                image,
                service,
            )
    else:
        logger.debug("Attempting to retrieve access token without credentials.")
        token = get_token(
            Client(opener=opener_factory(), base_url=authentication_url), image, service
        )
    return Client(
        opener=opener_factory(),
        # This package is built on version 2 of the Docker registry API.
        base_url=urljoin(registry_url, "/v2/"),
        token=token,
    )
