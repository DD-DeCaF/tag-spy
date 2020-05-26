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
from datetime import datetime, timezone
from operator import itemgetter
from typing import List
from urllib.parse import SplitResult, urlunsplit
from urllib.request import OpenerDirector

from .http_client import Client
from .http_helpers import get_response_json
from .image_tag_triple import ImageTagTriple


logger = logging.getLogger(__name__)


def get_token(client: Client, image: str, service: str) -> str:
    """
    Return an access token for the requested image and service.

    Args:
        client (Client): A client instance pointed at the authentication endpoint.
        image (str): The fully specified image name, for example, 'dddecaf/wsgi-base'.
        service (str): The URL of the service for which to request an access token.

    Returns:
        str: The access token which is valid for a pre-specified amount of time.

    Raises:
        urllib.error.URLError: In case of problems communicating with the registry.

    """
    logger.debug("Retrieving access token for image %r and service %r.", image, service)
    return str(
        client.get(
            params={"scope": f"repository:{image}:pull", "service": service}
        ).json()["token"]
    )


def verify_v2_capability(client: Client) -> None:
    """
    Verify that the registry API actually supports version 2.

    Args:
        client (Client): A client instance authenticated with a Bearer token and pointed
            at version 2 of the Docker registry API.

    Raises:
        urllib.error.HTTPError: In case the API does *not* support version 2.

    """
    logger.debug("Verifying version 2 API capability.")
    # The following statement will raise an HTTPError if the API does not support
    # version 2.
    # FIXME: Could be handled more nicely by raising an informative error.
    assert client.get().status == 200


def get_tags(client: Client, image: str) -> List[str]:
    """
    Return the list of tags for an image in its registry.

    Args:
        client (Client): A client instance authenticated with a Bearer token and pointed
            at version 2 of the Docker registry API.
        image (str): The fully specified image name, for example, 'dddecaf/wsgi-base'.

    Returns:
        list: All the tags as strings that were found.

    Raises:
        urllib.error.URLError: In case of problems communicating with the registry.

    """
    logger.debug("Retrieving image %r tags.", image)
    return [str(t) for t in client.get(path=f"{image}/tags/list").json()["tags"]]


def get_image_digest(client: Client, image: str, tag: str) -> str:
    """
    Return an image's digest from its manifest.

    Args:
        client (Client): A client instance authenticated with a Bearer token and pointed
            at version 2 of the Docker registry API.
        image (str): The fully specified image name, for example, 'dddecaf/wsgi-base'.
        tag (str): The base part of the tag that you are interested in, for
            example, 'alpine' will match 'dddecaf/wsgi-base:alpine_2020-04-28_24fe0a0'.

    Returns:
        str: The image's digest hash.

    Raises:
        urllib.error.URLError: In case of problems communicating with the registry.

    """
    logger.info("Retrieving image '%s:%s' digest.", image, tag)
    return str(client.get(path=f"{image}/manifests/{tag}").json()["config"]["digest"])


def get_image_timestamp(
    client: Client, image: str, digest: str, timestamp_label: str,
) -> datetime:
    """
    Return an image's build timestamp from its labels.

    Args:
        client (Client): A client instance authenticated with a Bearer token and pointed
            at version 2 of the Docker registry API.
        image (str): The fully specified image name, for example, 'dddecaf/wsgi-base'.
        digest (str): An image digest as can be retrieved from its manifest.
        timestamp_label (str): The image label that defines the build timestamp,
            for example, 'dk.dtu.biosustain.wsgi-base.alpine.build.timestamp'.

    Returns:
        datetime.datetime: The timestamp that records when the image was built.

    Raises:
        urllib.error.URLError: In case of problems communicating with the registry.

    See Also:
        get_image_digest

    """
    logger.info("Retrieving image %r configuration.", image)
    data = client.get(path=f"{image}/blobs/{digest}").json()
    try:
        timestamp = datetime.fromisoformat(data["config"]["Labels"][timestamp_label])
    except KeyError:
        logger.error(
            "The requested label '%s' does not exist. Ignoring. "
            "Possibilities are: %s.",
            timestamp_label,
            ", ".join(data["config"]["Labels"].keys()),
        )
        timestamp = datetime.fromtimestamp(0, timezone.utc)
    return timestamp


def get_latest_by_timestamp(
    client: Client, image: str, timestamp_label: str, tags: List[ImageTagTriple],
) -> ImageTagTriple:
    """
    Return the latest image tag as determined by the build timestamp.

    Args:
        client (Client): A client instance authenticated with a Bearer token and pointed
            at version 2 of the Docker registry API.
        image (str): The fully specified image name, for example, 'dddecaf/wsgi-base'.
        timestamp_label (str): The image label that defines the build timestamp,
            for example, 'dk.dtu.biosustain.wsgi-base.alpine.build.timestamp'.
        tags (list): A collection of ``ImageTagTriple`` that all contain the same date.

    Returns:
        ImageTagTriple: The latest of the collection.

    Raises:
        urllib.error.URLError: In case of problems communicating with the registry.

    """
    latest = []
    for triple in tags:
        digest = get_image_digest(client, image, str(triple))
        logger.debug("Digest: %s", digest)
        build_timestamp = get_image_timestamp(client, image, digest, timestamp_label)
        logger.debug("%s: %s", timestamp_label, build_timestamp)
        latest.append((triple, build_timestamp))
    latest.sort(key=itemgetter(1), reverse=True)
    return latest[0][0]
