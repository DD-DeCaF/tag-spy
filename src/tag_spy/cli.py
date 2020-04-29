# Copyright 2020 Novo Nordisk Foundation Center for Biosustainability,
# Technical University of Denmark.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Provide the main function to be used as an entry point for the CLI."""


import argparse
import logging

from .api import get_latest_tag


logger = logging.getLogger("tag_spy")


def main() -> None:
    """Define the console script entry point and thus the command line interface."""
    parser = argparse.ArgumentParser(description="Find the latest Docker image tag.")
    parser.add_argument(
        "image",
        metavar="IMAGE",
        help="A Docker image specification, for example, dddecaf/wsgi-base.",
    )
    parser.add_argument(
        "tag",
        metavar="BASE_TAG",
        help="The first part of an image tag. So if your tags have the format "
        "'<image>:<base>_<date>_<commit>', you should supply the <base> here.",
    )
    parser.add_argument(
        "label",
        metavar="LABEL",
        help="The name of the label that contains the build timestamp, for example,"
        " 'com.business.build.timestamp'.",
    )
    parser.add_argument(
        "--verbosity",
        help="The desired log level; either CRITICAL, ERROR, WARNING, INFO, or DEBUG "
        "(default WARNING).",
        default="WARNING",
    )
    args = parser.parse_args()
    logging.basicConfig(level=args.verbosity, format="[%(levelname)s] %(message)s")
    print(get_latest_tag(args.image, args.tag, args.label))
