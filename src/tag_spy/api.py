# Copyright 2020 Novo Nordisk Foundation Center for Biosustainability,
# Technical University of Denmark.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Provide public API functions for handling Docker image tags."""


import logging
from typing import Optional
from urllib.parse import urljoin

from .filter_helpers import filter_latest_matching
from .http_client import Client
from .http_helpers import build_authenticated_opener, build_authentication_opener
from .registry_helpers import (
    get_latest_by_timestamp,
    get_tags,
    get_token,
    verify_v2_capability,
)


logger = logging.getLogger(__name__)


def get_latest_tag(
    image: str,
    base_tag: str,
    authentication_url: str = "https://auth.docker.io/token",
    registry_url: str = "https://registry-1.docker.io",
    service: str = "registry.docker.io",
    username: Optional[str] = None,
    password: Optional[str] = None,
) -> str:
    """
    Parse the latest DD-DeCaF-specific tag of a Docker image from its registry.

    Args:
        image (str): The fully specified image name, for example, 'dddecaf/wsgi-base'.
        base_tag (str): The base part of the tag that you are interested in, for
            example, 'alpine' will match 'dddecaf/wsgi-base:alpine_2020-04-28_24fe0a0'.
        authentication_url (str, optional): The URL from where to retrieve an access
            token for the registry (the default https://auth.docker.io/token
            corresponds to Docker Hub).
        registry_url (str, optional): The URL of the registry API
            (default https://registry-1.docker.io).
        service (str, optional): The service URI for which to request an access
            token (default registry.docker.io).
        username (str, optional): A username used for authentication when
            retrieving an access token. Without a username no authentication will be
            attempted.
        password (str, optional): A password used for authentication when
            retrieving an access token. The password field may itself be a token for
            Bearer authentication when the username is 'oauth2accesstoken'.

    Returns:
        str: The very latest Docker image tag in its entirety.

    Raises:
        RuntimeError: If there are unexpected complications with the tags of the
            specified image.
        urllib.error.URLError: In case of problems communicating with the registry.

    """
    client = Client(
        opener=build_authentication_opener(registry_url, username, password),
        base_url=authentication_url,
    )
    token = get_token(client, image, service)
    client = Client(
        opener=build_authenticated_opener(token),
        # This package is built on version 2 of the Docker registry API.
        base_url=urljoin(registry_url, "/v2/"),
    )
    verify_v2_capability(client)
    tags = get_tags(client, image)
    if len(tags) == 0:
        raise RuntimeError(f"The requested image {image} does not have any tags.")
    try:
        latest_tags = filter_latest_matching(tags, base_tag)
    except ValueError:
        raise RuntimeError(
            f"The requested image {image} does not have any tags corresponding to the "
            f"expected format {base_tag}_<date>_<commit>."
        )
    if len(latest_tags) > 1:
        latest = get_latest_by_timestamp(client, image, latest_tags)
    elif len(latest_tags) == 1:
        latest = latest_tags[0]
    else:
        raise RuntimeError(
            f"The requested image {image} does not have any tags corresponding to the "
            f"expected format {base_tag}_<date>_<commit>."
        )
    return str(latest)
