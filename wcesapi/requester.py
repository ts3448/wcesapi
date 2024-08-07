import logging
from datetime import datetime
from urllib.parse import urljoin
import requests
import json
import time
from typing import Dict, Any, Optional, Literal

# HttpMethod type alias
HttpMethod = Literal["GET", "POST", "PUT", "DELETE", "PATCH"]

logger = logging.getLogger(__name__)


class RequesterError(Exception):
    """Base class for Requester exceptions."""

    pass


class UnauthorizedAccess(RequesterError):
    """Raised when the access token is invalid."""

    pass


class ResourceDoesNotExist(RequesterError):
    """Raised when the requested resource is not found."""

    pass


class UnprocessableEntity(RequesterError):
    """Raised when the request parameters are invalid."""

    pass


class Requester:
    """
    Responsible for handling HTTP requests to the Course Evaluations & Surveys API.

    Attributes:
        base_url (str): The base URL for the API.
        access_token (str): The access token for authentication.
        max_retries (Optional[int]): Maximum number of retry attempts for failed requests.
        retry_backoff (Optional[int]): Exponential backoff factor for retries (in seconds).
        rate_limit_delay (Optional[int]): Initial delay for rate limiting (in seconds).
    """

    def __init__(
        self,
        base_url: str,
        access_token: str,
        max_retries: Optional[int] = 3,
        retry_backoff: Optional[int] = 2,
        rate_limit_delay: Optional[int] = 1,
    ):
        """
        Initializes the Requester with the given parameters.

        Args:
            base_url (str): The base URL for the API.
            access_token (str): The access token for authentication.
            max_retries (Optional[int]): Maximum number of retry attempts for failed requests.
            retry_backoff (Optional[int]): Exponential backoff factor for retries (in seconds).
            rate_limit_delay (Optional[int]): Initial delay for rate limiting (in seconds).
        """
        self.original_url: str = base_url
        self.base_url = base_url + "/api/"
        self.access_token: str = access_token
        self.max_retries: int = max_retries if max_retries is not None else 3
        self.retry_backoff: int = retry_backoff if retry_backoff is not None else 2
        self.rate_limit_delay: int = (
            rate_limit_delay if rate_limit_delay is not None else 1
        )
        self._session = requests.Session()
        self._session.headers.update({"AuthToken": self.access_token})

    def set_retry_options(
        self, max_retries: Optional[int], retry_backoff: Optional[int]
    ):
        """
        Sets the retry options for the requester.

        Args:
            max_retries (Optional[int]): Maximum number of retry attempts for failed requests.
            retry_backoff (Optional[int]): Exponential backoff factor for retries (in seconds).
        """
        self.max_retries = max_retries if max_retries is not None else 3
        self.retry_backoff = retry_backoff if retry_backoff is not None else 2

    def set_rate_limit_delay(self, rate_limit_delay: Optional[int]):
        """
        Sets the rate limit delay for the requester.

        Args:
            rate_limit_delay (Optional[int]): Initial delay for rate limiting (in seconds).
        """
        self.rate_limit_delay = rate_limit_delay if rate_limit_delay is not None else 1

    def request(
        self,
        method: HttpMethod,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Makes a request to the Course Evaluations & Surveys API and returns the response.

        This method handles the entire request process, including retries for rate limiting.

        Args:
            method (HttpMethod): The HTTP method to use for the request.
            endpoint (str): The API endpoint to call.
            params (Optional[Dict[str, Any]]): Optional query parameters for GET requests.
            data (Optional[Dict[str, Any]]): Optional data for POST, PUT requests.

        Returns:
            Dict[str, Any]: The JSON-decoded response data.

        Raises:
            UnauthorizedAccess: If the access token is invalid.
            ResourceDoesNotExist: If the requested resource is not found.
            UnprocessableEntity: If the request parameters are invalid.
            RequesterError: For other HTTP errors or if all retries fail.
        """
        url = urljoin(self.base_url, endpoint)
        request_kwargs = self._prepare_request_kwargs(params, data)

        logger.info(f"Request: {method} {url}")
        logger.debug(f"Request data: {request_kwargs}")

        for attempt in range(self.max_retries):
            try:
                response = self._session.request(method, url, **request_kwargs)
                self._log_response(response)

                if response.status_code != 429:  # Not rate limited
                    self._handle_errors(response)
                    return self._parse_response(response)

                self._handle_rate_limit(attempt)
            except requests.RequestException as e:
                logger.error(f"Request failed on attempt {attempt + 1}: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise RequesterError(f"Request failed after all retries: {str(e)}")

        raise RequesterError("Request failed after all retries")

    def _prepare_request_kwargs(
        self,
        params: Optional[Dict[str, Any]],
        data: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Prepares the keyword arguments for the request.

        Args:
            params (Optional[Dict[str, Any]]): Optional query parameters.
            data (Optional[Dict[str, Any]]): Optional data for POST, PUT requests.

        Returns:
            Dict[str, Any]: Prepared keyword arguments.
        """
        request_kwargs = {}

        if params:
            request_kwargs["params"] = {
                k: self._format_value(v) for k, v in params.items()
            }

        if data:
            data = self._filter_none_values(data)
            request_kwargs["data"] = {k: self._format_value(v) for k, v in data.items()}
            self._session.headers.update(
                {"Content-Type": "application/x-www-form-urlencoded"}
            )
        return request_kwargs

    @staticmethod
    def _filter_none_values(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filters out None values from the data dictionary.

        Args:
            data (Dict[str, Any]): The data dictionary to filter.

        Returns:
            Dict[str, Any]: The filtered data dictionary without None values.
        """
        return {k: v for k, v in data.items() if v is not None}

    @staticmethod
    def _format_value(value: Any) -> str:
        """
        Formats the value for the API request.

        Args:
            value (Any): The value to format.

        Returns:
            str: The formatted value.
        """
        if isinstance(value, bool):
            return str(value).lower()
        elif isinstance(value, datetime):
            return value.isoformat()  # Ensure UTC format
        return str(value)

    def _parse_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Parses the response and returns the JSON-decoded data.

        Args:
            response (requests.Response): The HTTP response to parse.

        Returns:
            Dict[str, Any]: The JSON-decoded response data.
        """
        try:
            return response.json()
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON, returning raw text")
            return {"raw_text": response.text}

    def _calculate_rate_limit_delay(self, attempt: int) -> float:
        """
        Calculate the delay for rate limiting based on the attempt number.

        This method uses an exponential backoff strategy to determine
        the delay time for rate-limited requests.

        Args:
            attempt (int): The current attempt number (0-indexed).

        Returns:
            float: The calculated delay in seconds.
        """
        return self.rate_limit_delay * (self.retry_backoff**attempt)

    def _handle_rate_limit(self, attempt: int) -> None:
        """
        Handle rate limiting by implementing exponential backoff.

        This method calculates the appropriate delay using _calculate_rate_limit_delay,
        logs a warning message, and then waits for the calculated delay.

        Args:
            attempt (int): The current attempt number (0-indexed).

        Returns:
            None
        """
        retry_after = self._calculate_rate_limit_delay(attempt)
        logger.warning(f"Rate limited. Retrying after {retry_after} seconds.")
        time.sleep(retry_after)

    def _log_response(self, response: requests.Response) -> None:
        """
        Logs the response details.

        Args:
            response (requests.Response): The HTTP response to log.
        """
        logger.info(
            f"Response: {response.request.method} {response.url} {response.status_code}"
        )
        logger.debug(f"Response headers: {response.headers}")
        try:
            logger.debug(f"Response data: {response.json()}")
        except json.JSONDecodeError:
            logger.debug(f"Response data: {response.text}")

    def _handle_errors(self, response: requests.Response) -> None:
        """
        Handles errors in the response by raising appropriate exceptions.

        Args:
            response (requests.Response): The HTTP response to handle.

        Raises:
            UnauthorizedAccess: If the access token is invalid.
            ResourceDoesNotExist: If the requested resource was not found.
            UnprocessableEntity: If the request parameters are invalid.
            RequesterError: For other HTTP errors.
        """
        if response.status_code == 401:
            raise UnauthorizedAccess("The access token is invalid.")
        elif response.status_code == 404:
            raise ResourceDoesNotExist("The requested resource was not found.")
        elif response.status_code == 422:
            raise UnprocessableEntity("The request parameters are invalid.")
        elif response.status_code >= 400:
            raise RequesterError(f"HTTP error {response.status_code}: {response.text}")
