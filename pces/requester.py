import logging
from datetime import datetime
from urllib.parse import urljoin
import requests
import json
import time

from typing import Annotated, TypeAlias, Any, Dict, Optional, Literal

# Type aliases
HttpMethod: TypeAlias = Literal["GET", "POST", "PUT", "DELETE", "PATCH"]
ApiEndpoint: TypeAlias = Annotated[str, "The API endpoint to call"]
QueryParams: TypeAlias = Annotated[
    Dict[str, Any], "Optional query parameters for GET requests"
]
RequestData: TypeAlias = Annotated[
    Dict[str, Any], "Optional data for POST, PUT requests"
]
ResponseData: TypeAlias = Annotated[Dict[str, Any], "The JSON-decoded response data"]
MaxRetries: TypeAlias = Annotated[
    int | None, "Maximum number of retry attempts for failed requests"
]
RetryBackoff: TypeAlias = Annotated[
    int | None, "Exponential backoff factor for retries (in seconds)"
]
RateLimitDelay: TypeAlias = Annotated[
    int | None, "Initial delay for rate limiting (in seconds)"
]


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
    """

    def __init__(
        self,
        base_url: str,
        access_token: str,
        max_retries: MaxRetries,
        retry_backoff: RetryBackoff,
        rate_limit_delay: RateLimitDelay,
    ):
        self.base_url: str = base_url
        self.access_token: str = access_token
        self.max_retries: MaxRetries = max_retries
        self.retry_backoff: RetryBackoff = retry_backoff
        self.rate_limit_delay: RateLimitDelay = rate_limit_delay
        self._session = requests.Session()
        self._session.headers.update({"AuthToken": self.access_token})

    def set_retry_options(self, max_retries: MaxRetries, retry_backoff: RetryBackoff):
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff

    def set_rate_limit_delay(self, rate_limit_delay: RateLimitDelay):
        self.rate_limit_delay = rate_limit_delay

    def request(
        self,
        method: HttpMethod,
        endpoint: ApiEndpoint,
        params: QueryParams | None = None,
        data: RequestData | None = None,
    ) -> ResponseData:
        """
        Make a request to the Course Evaluations & Surveys API
        and return the response.

        Raises:
            UnauthorizedAccess: If the access token is invalid.
            ResourceDoesNotExist: If the requested resource is not found.
            UnprocessableEntity: If the request parameters are invalid.
            RequesterError: For other HTTP errors.
        """
        url = urljoin(self.base_url, endpoint)
        request_kwargs = self._prepare_request_kwargs(params, data)

        logger.info(f"Request: {method} {url}")
        logger.debug(f"Request data: {request_kwargs}")

        try:
            response = self._send_request(method, url, request_kwargs)
            self._log_response(response)
            self._handle_errors(response)
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise RequesterError(f"Request failed: {str(e)}")

    def _prepare_request_kwargs(
        self,
        params: Optional[Dict[str, Any]],
        data: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Prepares the keyword arguments for the request."""
        request_kwargs = {}

        if params:
            request_kwargs["params"] = {
                k: self._format_value(v) for k, v in params.items()
            }

        if data:
            request_kwargs["data"] = {k: self._format_value(v) for k, v in data.items()}
            self._session.headers.update(
                {"Content-Type": "application/x-www-form-urlencoded"}
            )

        return request_kwargs

    @staticmethod
    def _format_value(value: Any) -> str:
        """Format value for API request."""
        if isinstance(value, bool):
            return str(value).lower()
        elif isinstance(value, datetime):
            return value.isoformat() + "Z"  # Ensure UTC format
        return str(value)

    def _send_request(
        self, method: str, url: str, kwargs: Dict[str, Any]
    ) -> requests.Response:
        """Sends the HTTP request with retry logic."""
        for attempt in range(self.max_retries):
            response = self._session.request(method, url, **kwargs)
            if response.status_code != 429:  # Not rate limited
                return response
            self._handle_rate_limit(attempt)
        return response  # Return last response if all retries failed

    def _handle_rate_limit(self, attempt: int) -> None:
        """Handles rate limiting by implementing exponential backoff."""
        retry_after = self.rate_limit_delay * (self.retry_backoff**attempt)
        logger.warning(f"Rate limited. Retrying after {retry_after} seconds.")
        time.sleep(retry_after)

    def _log_response(self, response: requests.Response) -> None:
        """Logs the response details."""
        logger.info(
            f"Response: {response.request.method} {response.url} {response.status_code}"
        )
        logger.debug(f"Response headers: {response.headers}")
        try:
            logger.debug(f"Response data: {response.json()}")
        except json.JSONDecodeError:
            logger.debug(f"Response data: {response.text}")

    def _handle_errors(self, response: requests.Response) -> None:
        """Handles errors in the response by raising appropriate exceptions."""
        if response.status_code == 401:
            raise UnauthorizedAccess("The access token is invalid.")
        elif response.status_code == 404:
            raise ResourceDoesNotExist("The requested resource was not found.")
        elif response.status_code == 422:
            raise UnprocessableEntity("The request parameters are invalid.")
        elif response.status_code >= 400:
            raise RequesterError(f"HTTP error {response.status_code}: {response.text}")

    def __del__(self):
        """Ensures the session is closed when the Requester object is destroyed."""
        self._session.close()
