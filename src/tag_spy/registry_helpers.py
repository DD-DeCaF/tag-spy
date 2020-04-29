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


import json
import logging
from datetime import date, datetime
from typing import Dict, List, NamedTuple
from urllib.parse import SplitResult, urlencode, urlunsplit
from urllib.request import Request, urlopen


logger = logging.getLogger(__name__)


class ImageTagTriple(NamedTuple):
    """Define a minimal class for storing complete tag information."""

    base: str
    date: date
    commit: str

    def __str__(self):
        """Return a string representation of the tag triple."""
        return f"{self.base}_{self.date.isoformat()}_{self.commit}"


def get_token(parts: SplitResult, image: str, service: str) -> str:
    """
    Return an access token for the requested image and service.

    Args:
        parts (urllib.parse.SplitResult): The separate parts of the authentication URL
            as returned by ``urlsplit``.
        image (str): The fully specified image name, for example, 'dddecaf/wsgi-base'.
        service (str): The URL of the service for which to request an access token.

    Returns:
        str: The access token which is valid for a pre-specified amount of time.

    Raises:
        urllib.error.URLError: In case of problems communicating with the registry.

    """
    params = {"scope": f"repository:{image}:pull", "service": service}
    url = urlunsplit(parts._replace(query=urlencode(params)))
    logger.debug("Retrieving token at %r.", url)
    request = Request(url)
    with urlopen(request) as response:
        content = response.read()
        logger.debug("%s", content)
    data = json.loads(content)
    return str(data["access_token"])


def verify_v2_capability(parts: SplitResult, headers: Dict[str, str]) -> None:
    """
    Verify that the registry API actually supports version 2.

    Args:
        parts (urllib.parse.SplitResult): The separate parts of the registry API URL
            as returned by ``urlsplit``.
        headers (dict): A map defining HTTP headers. They must include an 'Accept'
            header and an 'Authorization' header with a bearer token.

    Raises:
        urllib.error.URLError: In case the API does *not* support version 2.

    """
    url = urlunsplit(parts._replace(path="/v2/"))
    logger.debug("Verifying version 2 API capability at %r.", url)
    request = Request(url, headers=headers)
    # The following statement will raise an URLError if the API does not support
    # version 2.
    with urlopen(request) as response:
        assert response.status == 200


def get_tags(parts: SplitResult, headers: Dict[str, str], image: str) -> List[str]:
    """
    Return the list of tags for an image in its registry.

    Args:
        parts (urllib.parse.SplitResult): The separate parts of the registry API URL
            as returned by ``urlsplit``.
        headers (dict): A map defining HTTP headers. They must include an 'Accept'
            header and an 'Authorization' header with a bearer token.
        image (str): The fully specified image name, for example, 'dddecaf/wsgi-base'.

    Returns:
        list: All the tags as strings that were found.

    Raises:
        urllib.error.URLError: In case of problems communicating with the registry.

    """
    url = urlunsplit(parts._replace(path=f"/v2/{image}/tags/list"))
    logger.debug("Retrieving image %r tags from %r.", image, url)
    request = Request(url, headers=headers)
    with urlopen(request) as response:
        content = response.read()
        logger.debug("%s", content)
    data = json.loads(content)
    return [str(t) for t in data["tags"]]


def get_image_digest(
    parts: SplitResult, headers: Dict[str, str], image: str, tag: str
) -> str:
    """
    Return an image's digest from its manifest.

    Args:
        parts (urllib.parse.SplitResult): The separate parts of the registry API URL
            as returned by ``urlsplit``.
        headers (dict): A map defining HTTP headers. They must include an 'Accept'
            header and an 'Authorization' header with a bearer token.
        image (str): The fully specified image name, for example, 'dddecaf/wsgi-base'.
        tag (str): The base part of the tag that you are interested in, for
            example, 'alpine' will match 'dddecaf/wsgi-base:alpine_2020-04-28_24fe0a0'.

    Returns:
        str: The image's digest hash.

    Raises:
        urllib.error.URLError: In case of problems communicating with the registry.

    """
    url = urlunsplit(parts._replace(path=f"/v2/{image}/manifests/{tag}"))
    logger.info("Retrieving image %r digest from %r.", image, url)
    request = Request(url, headers=headers)
    with urlopen(request) as response:
        content = response.read()
        logger.debug("%s", content)
    data = json.loads(content)
    return str(data["config"]["digest"])


def get_image_timestamp(
    parts: SplitResult,
    headers: Dict[str, str],
    image: str,
    digest: str,
    timestamp_label: str,
) -> datetime:
    """
    Return an image's build timestamp from its labels.

    Args:
        parts (urllib.parse.SplitResult): The separate parts of the registry API URL
            as returned by ``urlsplit``.
        headers (dict): A map defining HTTP headers. They must include an 'Accept'
            header and an 'Authorization' header with a bearer token.
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
    url = urlunsplit(parts._replace(path=f"/v2/{image}/blobs/{digest}"))
    logger.info("Retrieving image %r configuration from %r.", image, url)
    request = Request(url, headers=headers)
    with urlopen(request) as response:
        content = response.read()
        logger.debug("%s", content)
    data = json.loads(content)
    return datetime.fromisoformat(data["config"]["Labels"][timestamp_label])
