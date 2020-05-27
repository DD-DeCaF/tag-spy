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


"""Test that the HTTP client can properly authenticate a user."""


import pytest

from tag_spy.http_client import Client
from tag_spy.opener_factory import basic_authentication_opener_factory, opener_factory
from tag_spy.registry_helpers import get_token


@pytest.mark.parametrize("username, password", [("foo", "bar")])
def test_httpbin_basic_authentication(username: str, password: str):
    """Expect that basic authentication is successful on httpbin.org."""
    client = Client(
        opener=basic_authentication_opener_factory(
            "https://httpbin.org", username, password
        ),
        base_url="https://httpbin.org",
    )
    response = client.get(path=f"/basic-auth/{username}/{password}")
    assert response.status == 200


def test_docker_hub_public():
    """Expect that Docker Hub issues an access token without authentication."""
    client = Client(opener=opener_factory(), base_url="https://auth.docker.io/token")
    token = get_token(client, "dddecaf/wsgi-base", "registry.docker.io")
    assert len(token) > 0
