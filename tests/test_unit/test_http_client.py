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


"""Test the behaviour of the HTTP client."""


from typing import Dict, Optional
from urllib.request import OpenerDirector, build_opener

import pytest

from tag_spy.http_client import Client


@pytest.fixture(scope="function")
def opener() -> OpenerDirector:
    """Return an HTTP opener instance."""
    return build_opener()


@pytest.mark.parametrize(
    "path, params, expected",
    [
        (None, None, "https://example.com/"),
        ("/gzip", None, "https://example.com/gzip"),
        ("deflate/this", None, "https://example.com/deflate/this"),
        (None, {"once": "twice"}, "https://example.com/?once=twice"),
        ("foo", {"once": "twice"}, "https://example.com/foo?once=twice"),
    ],
)
def test_client_url_composition(
    opener, path: Optional[str], params: Optional[Dict[str, str]], expected: str
) -> None:
    """Test that the HTTP client correctly builds URLs."""
    client = Client(opener=opener, base_url="https://example.com/")
    assert client._build_url(path=path, params=params) == expected
