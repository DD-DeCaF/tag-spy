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


"""Define helpers that interact with a Docker registry."""


import logging
from datetime import date
from itertools import takewhile
from operator import itemgetter
from typing import Dict, List
from urllib.parse import SplitResult

from .registry_helpers import ImageTagTriple, get_image_digest, get_image_timestamp


logger = logging.getLogger(__name__)


def filter_latest_matching(all_tags: List[str], tag_part: str) -> List[ImageTagTriple]:
    """
    Return those tags that correspond to the expected format.

    Args:
        all_tags (list): All the tags as strings.
        tag_part (str): The base part of the tag that you are interested in, for
            example, 'alpine' will match 'dddecaf/wsgi-base:alpine_2020-04-28_24fe0a0'.

    Returns:
        list: A collection of ``ImageTagTriple`` instances.

    Raises:
        ValueError: In case no tags correspond to the expected format.

    """
    tags = []
    for tag in all_tags:
        try:
            base, build_date, build_commit = tag.split("_")
        except ValueError:
            continue
        if base == tag_part:
            tags.append(
                ImageTagTriple(base, date.fromisoformat(build_date), build_commit)
            )
    if len(tags) == 0:
        raise ValueError("No tags after filtering.")
    # Order tags with the latest date first.
    tags.sort(key=itemgetter(1), reverse=True)
    # Collect all tags created on the latest day.
    latest = tags[0].date
    return list(takewhile(lambda triple: triple.date == latest, tags))


def get_latest_by_timestamp(
    parts: SplitResult,
    headers: Dict[str, str],
    image: str,
    timestamp_label: str,
    tags: List[ImageTagTriple],
) -> ImageTagTriple:
    """
    Return the latest image tag as determined by the build timestamp.

    Args:
        parts (urllib.parse.SplitResult): The separate parts of the registry API URL
            as returned by ``urlsplit``.
        headers (dict): A map defining HTTP headers. They must include an 'Accept'
            header and an 'Authorization' header with a bearer token.
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
        digest = get_image_digest(parts, headers, image, str(triple))
        logger.debug("Digest: %s", digest)
        build_timestamp = get_image_timestamp(
            parts, headers, image, digest, timestamp_label
        )
        logger.debug("%s: %s", timestamp_label, build_timestamp)
        latest.append((triple, build_timestamp))
    latest.sort(key=itemgetter(1), reverse=True)
    return latest[0][0]
