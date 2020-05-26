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


"""Test """


from typing import Dict, Optional
from urllib.request import build_opener

import pytest

from tag_spy.http_client import Client


@pytest.fixture()
def client() -> Client:
    return Client(opener=build_opener(), base_url="https://httpbin.org/")


@pytest.mark.parametrize(
    "path, params, expected",
    [
        (None, None, "https://httpbin.org/"),
        ("/gzip", None, "https://httpbin.org/gzip"),
        ("deflate/this", None, "https://httpbin.org/deflate/this"),
        (None, {"once": "twice"}, "https://httpbin.org/?once=twice"),
    ],
)
def test_from_tag(
    client, path: Optional[str], params: Optional[Dict[str, str]], expected: str
) -> None:
    """Test that ."""
    assert client._url(path=path, params=params) == expected
