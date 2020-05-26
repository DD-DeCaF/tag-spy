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
import sys
from getpass import getpass
from typing import Optional

from . import __version__
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
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "--verbosity",
        help="The desired log level (default WARNING).",
        choices=("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"),
        default="WARNING",
    )
    parser.add_argument(
        "--authentication",
        metavar="URL",
        help="The URL from where to retrieve an access token for the registry "
        "(the default https://auth.docker.io/token corresponds to Docker Hub).",
        default="https://auth.docker.io/token",
    )
    parser.add_argument(
        "--registry",
        metavar="URL",
        help="The URL of the container registry API "
        "(default https://registry-1.docker.io).",
        default="https://registry-1.docker.io",
    )
    parser.add_argument(
        "--service",
        metavar="URI",
        help="The service URI for which to request an access token "
        "(default registry.docker.io).",
        default="registry.docker.io",
    )
    parser.add_argument(
        "--username",
        metavar="STR",
        help="A username used for authentication when retrieving an access token. "
        "Without a username no authentication will be attempted.",
        default=None,
    )
    parser.add_argument(
        "--password",
        action="store_true",
        help="A password will be requested interactively. It is used for "
        "authentication when retrieving an access token.The password field may "
        "itself be a token for Bearer authentication when the username is "
        "'oauth2accesstoken'.",
    )
    parser.add_argument(
        "--password-stdin",
        action="store_true",
        help="A password will be read from standard input. It is used for "
        "authentication when retrieving an access token.The password field may "
        "itself be a token for Bearer authentication when the username is "
        "'oauth2accesstoken'.",
    )
    args = parser.parse_args()
    logging.basicConfig(level=args.verbosity, format="[%(levelname)s] %(message)s")
    if args.password_stdin:
        password: Optional[str] = sys.stdin.read().rstrip("\r\n")
    else:
        password = getpass() if args.password else None
    print(
        get_latest_tag(
            image=args.image,
            base_tag=args.tag,
            authentication_url=args.authentication,
            registry_url=args.registry,
            service=args.service,
            username=args.username,
            password=password,
        )
    )
