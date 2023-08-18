import logging
from datetime import datetime
from pprint import pformat

import requests
from errors import (
    UnauthorizedAccess,
    ResourceDoesNotExist,
    UnprocessableEntity,
    GeneralError)

logger = logging.getLogger(__name__)


class Requester(object):
    """
    Responsible for handling HTTP requests.
    """

    def __init__(self, base_url, access_token):
        """
        :param base_url: The base URL of the CES instance's API.
        :type base_url: str
        :param access_token: The API key to authenticate requests with.
        :type access_token: str
        """
        # Preserve the original base url and add "/api/v1" to it
        self.original_url = base_url
        self.base_url = base_url + "/api/"
        self.access_token = access_token
        self._session = requests.Session()
        self._cache = []

    def _delete_request(self, url, headers, data=None, **kwargs):
        """
        Issue a DELETE request to the specified endpoint with the data provided.

        :param url: The URL to request.
        :type url: str
        :param headers: The HTTP headers to send with this request.
        :type headers: dict
        :param data: The data to send with this request.
        :type data: dict
        """
        return self._session.delete(url, headers=headers, data=data)

    def _get_request(self, url, headers, params=None, **kwargs):
        """
        Issue a GET request to the specified endpoint with the data provided.

        :param url: The URL to request.
        :type url: str
        :param headers: The HTTP headers to send with this request.
        :type headers: dict
        :param params: The parameters to send with this request.
        :type params: dict
        """
        return self._session.get(url, headers=headers, params=params)

    def _patch_request(self, url, headers, data=None, **kwargs):
        """
        Issue a PATCH request to the specified endpoint with the data provided.

        :param url: The URL to request.
        :type url: str
        :param headers: The HTTP headers to send with this request.
        :type headers: dict
        :param data: The data to send with this request.
        :type data: dict
        """
        return self._session.patch(url, headers=headers, data=data)

    def _post_request(self, url, headers, data=None, json=False):
        """
        Issue a POST request to the specified endpoint with the data provided.

        :param url: The URL to request.
        :type url: str
        :param headers: The HTTP headers to send with this request.
        :type headers: dict
        :param data: The data to send with this request.
        :type data: dict
        :param json: Whether or not to send the data as json
        :type json: bool
        """
        if json:
            return self._session.post(url, headers=headers, json=dict(data))

        # Grab file from data.
        files = None
        for field, value in data:
            if field == "file":
                if isinstance(value, dict) or value is None:
                    files = value
                else:
                    files = {"file": value}
                break

        # Remove file entry from data.
        data[:] = [tup for tup in data if tup[0] != "file"]

        return self._session.post(url, headers=headers, data=data, files=files)

    def _put_request(self, url, headers, data=None, **kwargs):
        """
        Issue a PUT request to the specified endpoint with the data provided.

        :param url: The URL to request.
        :type url: str
        :param headers: The HTTP headers to send with this request.
        :type headers: dict
        :param data: The data to send with this request.
        :type data: dict
        """
        return self._session.put(url, headers=headers, data=data)

    def request(
        self,
        method,
        endpoint=None,
        headers=None,
        use_auth=True,
        _url=None,
        _kwargs=None,
        json=False,
        **kwargs
    ):
        """
        Make a request to the CES API and return the response.

        :param method: The HTTP method for the request.
        :type method: str
        :param endpoint: The endpoint to call.
        :type endpoint: str
        :param headers: Optional HTTP headers to be sent with the request.
        :type headers: dict
        :param use_auth: Optional flag to remove the authentication
            header from the request.
        :type use_auth: bool
        :param _kwargs: A list of 2-tuples representing processed
            keyword arguments to be sent to Canvas as params or data.
        :type _kwargs: `list`
        :param json: Whether or not to treat the data as json instead of form data.
            currently only the POST request of GraphQL is using this parameter.
            For all other methods it's just passed and ignored.
        :type json: `bool`
        :rtype: :class:`requests.Response`
        """
        full_url = _url if _url else "{}{}".format(self.base_url, endpoint)

        if not headers:
            headers = {}

        if use_auth:
            auth_header = {"AuthToken": "{}".format(self.access_token)}
            headers.update(auth_header)

        # Convert kwargs into list of 2-tuples and combine with _kwargs.
        _kwargs = _kwargs or []
        _kwargs.extend(kwargs.items())

        # Do any final argument processing before sending to request method.
        for i, kwarg in enumerate(_kwargs):
            kw, arg = kwarg

            # Convert boolean objects to a lowercase string.
            if isinstance(arg, bool):
                _kwargs[i] = (kw, str(arg).lower())

            # Convert any datetime objects into ISO 8601 formatted strings.
            elif isinstance(arg, datetime):
                _kwargs[i] = (kw, arg.isoformat())

        # Determine the appropriate request method.
        if method == "GET":
            req_method = self._get_request
        elif method == "POST":
            req_method = self._post_request
        elif method == "DELETE":
            req_method = self._delete_request
        elif method == "PUT":
            req_method = self._put_request
        elif method == "PATCH":
            req_method = self._patch_request

        # Call the request method
        logger.info("Request: {method} {url}".format(method=method, url=full_url))


        if _kwargs:
            logger.debug("Data: {data}".format(data=pformat(_kwargs)))

        response = req_method(full_url, headers, _kwargs, json=json)
        logger.info(
            "Response: {method} {url} {status}".format(
                method=method, url=full_url, status=response.status_code
            )
        )
        logger.debug(
            "Headers: {headers}"
        )
        

        try:
            logger.debug(
                "Data: {data}".format(data=pformat(response.content.decode("utf-8")))
            )
        except UnicodeDecodeError:
            logger.debug("Data: {data}".format(data=pformat(response.content)))
        except AttributeError:
            # response.content is None
            logger.debug("No data")

        # Add response to internal cache
        if len(self._cache) > 4:
            self._cache.pop()

            self._cache.insert(0, response)

        # Raise for status codes
        if response.status_code == 401:
            raise UnauthorizedAccess("The token is not valid.")
        elif response.status_code == 404:
            raise ResourceDoesNotExist("The requested resource is not found.")
        elif response.status_code == 422:
            raise UnprocessableEntity("The request parameters are not valid.")
        elif response.status_code > 400:
            # generic catch-all for error codes
            raise GeneralError(
                "Encountered an error: status code {}".format(response.status_code)
            )

        return response
