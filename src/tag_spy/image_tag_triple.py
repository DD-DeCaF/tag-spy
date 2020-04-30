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


"""Provide a representation of a Docker image tag triple."""


from __future__ import annotations

from datetime import date
from typing import NamedTuple


class ImageTagTriple(NamedTuple):
    """Define a minimal class for storing complete tag information."""

    base: str
    date: date
    commit: str

    def __str__(self) -> str:
        """Return a string representation of the tag triple."""
        return f"{self.base}_{self.date.isoformat()}_{self.commit}"

    @classmethod
    def from_tag(cls, tag: str) -> ImageTagTriple:
        """
        Create a tag triple representation from a complete image tag.

        Args:
            tag (str): A Docker image tag of the form '<base>_<date>_<commit>'.

        Returns:
            ImageTagTriple: A new instance with separate tag parts.

        Raises:
            ValueError: In case the tag does not conform with the triple format or the
                <date> is not in iso-8601 format.

        """
        base, build_date, build_commit = tag.split("_")
        return cls(base=base, date=date.fromisoformat(build_date), commit=build_commit)
