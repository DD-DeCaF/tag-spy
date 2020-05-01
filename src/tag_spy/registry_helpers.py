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
from urllib.parse import SplitResult, urlencode, urlunsplit
from urllib.request import OpenerDirector

from .http_helpers import get_response_json
from .image_tag_triple import ImageTagTriple


logger = logging.getLogger(__name__)


def get_token(
    opener: OpenerDirector, parts: SplitResult, image: str, service: str
) -> str:
    """
    Return an access token for the requested image and service.

    Args:
        opener (urllib.request.OpenerDirector): The opener with attached handlers and
            headers for calling the URL.
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
    data = get_response_json(opener, url)
    return str(data["token"])


def verify_v2_capability(opener: OpenerDirector, parts: SplitResult) -> None:
    """
    Verify that the registry API actually supports version 2.

    Args:
        opener (urllib.request.OpenerDirector): The opener with attached handlers and
            headers for calling the URL.
        parts (urllib.parse.SplitResult): The separate parts of the registry API URL
            as returned by ``urlsplit``.

    Raises:
        urllib.error.URLError: In case the API does *not* support version 2.

    """
    url = urlunsplit(parts._replace(path="/v2/"))
    logger.debug("Verifying version 2 API capability at %r.", url)
    # The following statement will raise an URLError if the API does not support
    # version 2.
    # FIXME: Could be handled more nicely by raising an informative error.
    with opener.open(url) as response:
        assert response.status == 200


def get_tags(opener: OpenerDirector, parts: SplitResult, image: str) -> List[str]:
    """
    Return the list of tags for an image in its registry.

    Args:
        opener (urllib.request.OpenerDirector): The opener with attached handlers and
            headers for calling the URL.
        parts (urllib.parse.SplitResult): The separate parts of the registry API URL
            as returned by ``urlsplit``.
        image (str): The fully specified image name, for example, 'dddecaf/wsgi-base'.

    Returns:
        list: All the tags as strings that were found.

    Raises:
        urllib.error.URLError: In case of problems communicating with the registry.

    """
    url = urlunsplit(parts._replace(path=f"/v2/{image}/tags/list"))
    logger.debug("Retrieving image %r tags from %r.", image, url)
    logger.debug("%r", opener.addheaders)
    data = get_response_json(opener, url)
    return [str(t) for t in data["tags"]]


def get_image_digest(
    opener: OpenerDirector, parts: SplitResult, image: str, tag: str
) -> str:
    """
    Return an image's digest from its manifest.

    Args:
        opener (urllib.request.OpenerDirector): The opener with attached handlers and
            headers for calling the URL.
        parts (urllib.parse.SplitResult): The separate parts of the registry API URL
            as returned by ``urlsplit``.
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
    data = get_response_json(opener, url)
    return str(data["config"]["digest"])


def get_image_timestamp(
    opener: OpenerDirector,
    parts: SplitResult,
    image: str,
    digest: str,
    timestamp_label: str,
) -> datetime:
    """
    Return an image's build timestamp from its labels.

    Args:
        opener (urllib.request.OpenerDirector): The opener with attached handlers and
            headers for calling the URL.
        parts (urllib.parse.SplitResult): The separate parts of the registry API URL
            as returned by ``urlsplit``.
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
    data = get_response_json(opener, url)
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
    opener: OpenerDirector,
    parts: SplitResult,
    image: str,
    timestamp_label: str,
    tags: List[ImageTagTriple],
) -> ImageTagTriple:
    """
    Return the latest image tag as determined by the build timestamp.

    Args:
        opener (urllib.request.OpenerDirector): The opener with attached handlers and
            headers for calling the URL.
        parts (urllib.parse.SplitResult): The separate parts of the registry API URL
            as returned by ``urlsplit``.
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
        digest = get_image_digest(opener, parts, image, str(triple))
        logger.debug("Digest: %s", digest)
        build_timestamp = get_image_timestamp(
            opener, parts, image, digest, timestamp_label
        )
        logger.debug("%s: %s", timestamp_label, build_timestamp)
        latest.append((triple, build_timestamp))
    latest.sort(key=itemgetter(1), reverse=True)
    return latest[0][0]
