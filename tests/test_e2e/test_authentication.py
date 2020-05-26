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


"""Test that ."""


import pytest

from tag_spy.http_client import Client
from tag_spy.http_helpers import build_authentication_opener
from tag_spy.registry_helpers import get_token


@pytest.mark.parametrize("username, password", [("foo", "bar")])
def test_basic_authentication(username: str, password: str):
    """Expect that ."""
    client = Client(
        opener=build_authentication_opener("https://httpbin.org", username, password),
        base_url="https://httpbin.org",
    )
    response = client.get(path=f"/basic-auth/{username}/{password}")
    assert response.status == 200


def test_docker_hub():
    auth_opener = build_authentication_opener(
        "https://registry-1.docker.io", None, None
    )
    client = Client(opener=auth_opener, base_url="https://auth.docker.io/token")
    token = get_token(client, "dddecaf/wsgi-base", "registry.docker.io")
    assert len(token) > 0
