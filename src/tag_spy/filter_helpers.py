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
from itertools import takewhile
from operator import itemgetter
from typing import List

from .image_tag_triple import ImageTagTriple


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
            triple = ImageTagTriple.from_tag(tag)
        except ValueError:
            continue
        if triple.base == tag_part:
            tags.append(triple)
    if len(tags) == 0:
        raise ValueError("No tags after filtering.")
    # Order tags with the latest date first.
    tags.sort(key=itemgetter(1), reverse=True)
    # Collect all tags created on the latest day.
    latest = tags[0].date
    return list(takewhile(lambda triple: triple.date == latest, tags))
