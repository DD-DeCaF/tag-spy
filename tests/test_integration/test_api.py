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


"""Test that the public package interface is consistent."""


from importlib import import_module

import pytest


@pytest.mark.parametrize(
    "public_module, symbol", [("tag_spy", "get_latest_tag"), ("tag_spy.cli", "main")]
)
def test_public_api(public_module, symbol):
    """Expect that objects as given by the parameters can be imported."""
    public_module = import_module(public_module)
    assert hasattr(public_module, symbol)
