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


"""Provide an HTTP client for making requests."""


import gzip
import json
import logging
import zlib
from http.client import HTTPResponse
from typing import Dict, List, Optional, Union
from urllib.parse import urlencode, urljoin, urlsplit, urlunsplit
from urllib.request import OpenerDirector


logger = logging.getLogger(__name__)


class Response:
    """
    Define an HTTP response class.

    This class should not have to be instantiated directly.

    Attributes:
        status (int): The numeric HTTP status code of the response.
        body (bytes): The raw body of the response as bytes.

    Methods:
        json: Deserialize the response's body as JSON and return the object.

    """

    def __init__(self, *, response: HTTPResponse, **kwargs) -> None:
        """
        Initialize an HTTP response object.

        Args:
            response (http.client.HTTPResponse): A standard library response that is
                wrapped by this object.
            **kwargs: Passed to parent classes.
        """
        super().__init__(**kwargs)  # type: ignore
        self._response = response
        # Immediately read the body while the response context is still available.
        self._body = self._content()

    def _content(self) -> bytes:
        """Return the response body and decompress it if required."""
        if self._response.getheader("Content-Encoding", "").lower() == "gzip":
            return gzip.decompress(self._response.read())
        elif self._response.getheader("Content-Encoding", "").lower() == "deflate":
            return zlib.decompress(self._response.read())
        else:
            return self._response.read()

    @property
    def status(self) -> int:
        """Get the response's HTTP status code."""
        return self._response.status

    @property
    def body(self) -> bytes:
        """Get the response's raw body content as bytes."""
        return self._body

    def json(self) -> Union[Dict, List, str]:
        """Deserialize the response's body as JSON and return the object."""
        if len(self.body) == 0:
            return ""
        try:
            return json.loads(self.body)  # type: ignore
        except json.JSONDecodeError:
            logger.debug(self.body)
            raise


class Client:
    """
    Define an HTTP client for making requests.

    Methods:
        get: Make an HTTP GET request and return the response.

    """

    def __init__(self, *, opener: OpenerDirector, base_url: str, **kwargs) -> None:
        """
        Initialize an HTTP client with a base URL.

        Args:
            opener (urllib.request.OpenerDirector): The opener with attached handlers
                and headers for calling the URL.
            base_url (str): The base URL for all future requests.
            **kwargs: Passed to parent constructors.

        """
        super().__init__(**kwargs)  # type: ignore
        self._opener = opener
        self._parts = urlsplit(base_url)

    def _build_url(
        self, path: Optional[str] = None, params: Optional[Dict[str, str]] = None,
    ) -> str:
        """Construct a correctly encoded URL from its parts."""
        result = self._parts
        if path is not None:
            result = result._replace(path=urljoin(result.path, path))
        if params is not None:
            result = result._replace(query=urlencode(params))
        return urlunsplit(result)

    def get(
        self,
        path: Optional[str] = None,
        params: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Response:
        """
        Make an HTTP GET request and return the response.

        Args:
            path (str, optional): An optional relative or absolute URL path to modify
                the base URL.
            params (dict, optional): An optional mapping from query parameter names to
                their values.

        Returns:
            Response: An HTTP response instance.

        """

        logger.debug("Making GET request to %r.", self._build_url(path, params))
        with self._opener.open(self._build_url(path, params), **kwargs) as response:
            logger.debug("%d %s", response.status, response.reason)
            logger.debug("%r", response.getheaders())
            # Must be returned within the context such that the response body is
            # available for reading.
            return Response(response=response)
