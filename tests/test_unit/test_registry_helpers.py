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


"""Test the expected outcomes of helper functions."""


from typing import Tuple

import pytest

from tag_spy.registry_helpers import parse_iso_8601_timestamp


@pytest.mark.parametrize(
    "timestamp, expected",
    [
        ("2020-04-29T12:14:30.0+02:00", (2020, 4, 29, 10, 14, 30)),
        ("2020-04-29T10:14:30.0+00:00", (2020, 4, 29, 10, 14, 30)),
        ("2020-04-29T08:14:30.0-02:00", (2020, 4, 29, 10, 14, 30)),
        ("2020-04-29T10:14:30.00Z", (2020, 4, 29, 10, 14, 30)),
        ("2020-04-29T10:14:30.755675967Z", (2020, 4, 29, 10, 14, 30)),
        ("2020-04-29T10:14:30.755675967+00:00", (2020, 4, 29, 10, 14, 30)),
        ("2020-04-29T08:14:30.755675967-02:00", (2020, 4, 29, 10, 14, 30)),
    ],
)
def test_timestamp_parsing(timestamp: str, expected: Tuple[int, ...]) -> None:
    """Expect timestamps of the format used in DD-DeCaF to be parsed correctly."""
    assert parse_iso_8601_timestamp(timestamp).utctimetuple()[:6] == expected
