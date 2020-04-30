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


"""Test the expected behaviour of the image tag triple."""


from datetime import date
from typing import Tuple

import pytest

from tag_spy.image_tag_triple import ImageTagTriple


@pytest.mark.parametrize(
    "tag, expected",
    [
        pytest.param(
            "latest",
            None,
            marks=pytest.mark.raises(
                exception=ValueError, message="not enough values to unpack"
            ),
        ),
        pytest.param(
            "latest_2020_abcdefg",
            None,
            marks=pytest.mark.raises(
                exception=ValueError, message="Invalid isoformat string"
            ),
        ),
        ("latest_2020-04-29_abcdefg", ("latest", date(2020, 4, 29), "abcdefg")),
    ],
)
def test_from_tag(tag: str, expected: Tuple) -> None:
    """Test that image tag triples of the correct format are initialized."""
    triple = ImageTagTriple.from_tag(tag)
    assert triple == expected


@pytest.mark.parametrize(
    "triple, expected",
    [
        (
            ImageTagTriple("latest", date(2020, 4, 29), "abcdefg"),
            "latest_2020-04-29_abcdefg",
        )
    ],
)
def test_dunder_str(triple: ImageTagTriple, expected: str) -> None:
    """Test that an image tag triple correctly serializes as string."""
    assert str(triple) == expected
