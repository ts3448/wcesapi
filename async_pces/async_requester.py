from datetime import datetime
import logging
import aiohttp
import asyncio
from pprint import pformat
import math
from urllib.parse import urlencode
from async_util import clean_headers
from pces.async_pces.exceptions import BadRequest, Conflict, Forbidden, InvalidAccessToken, RateLimitExceeded, ResourceDoesNotExist, Unauthorized, UnprocessableEntity


logger = logging.getLogger(__name__)


class AsyncRequester:
    def __init__(
            self,
            base_url,
            access_token,
            max_concurrent_requests=200,
            rate_limit_threshold=200,
            timeout=10
    ):
        self.original_url = base_url
        self.base_url = base_url + "/api/"
        self.access_token = access_token
        self.rate_limit_remaining = 700  # Default rate limit
        self.rate_limit_threshold = rate_limit_threshold
        self.timeout = timeout
        self._session = None
        self._semaphore = asyncio.Semaphore(max_concurrent_requests)

    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        self._session = aiohttp.ClientSession(timeout=timeout)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._session.close()

    async def _delete_request(self, url, headers, data=None, **kwargs):
        return await self._session.delete(url, headers=headers, data=data)

    async def _get_request(self, url, headers, params=None, **kwargs):
        return await self._session.get(url, headers=headers, params=params)

    async def _patch_request(self, url, headers, data=None, **kwargs):
        return await self._session.patch(url, headers=headers, data=data)

    async def _post_request(self, url, headers, data=None, json=False):
        if json:
            return await self._session.post(url, headers=headers, json=dict(data))

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

        return await self._session.post(url, headers=headers, data=data, files=files)

    async def _put_request(self, url, headers, data=None, **kwargs):
        return await self._session.put(url, headers=headers, data=data)

    async def request(
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
        await self.apply_rate_limit_pullback()

        async with self._semaphore:  # Acquire semaphore

            full_url = _url if _url else "{}{}".format(self.base_url, endpoint)

            if not headers:
                headers = {}

            if use_auth:
                auth_header = {"Authorization": "Bearer {}".format(self.access_token)}
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
            try:
                logger.info("Request: {method} {url}".format(method=method, url=full_url))
                logger.debug(
                    "Headers: {headers}".format(headers=pformat(clean_headers(headers)))
                )

                if _kwargs:
                    logger.debug("Data: {data}".format(data=pformat(_kwargs)))
                                              
                response = await req_method(full_url, headers, _kwargs, json=json)

                logger.info(
                    "Response: {method} {url} {status}".format(
                        method=method, url=full_url, status=response.status
                    )
                )
                logger.debug(
                    "Headers: {headers}".format(
                        headers=pformat(clean_headers(response.headers))
                    )
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


                # Raise for status codes
                if response.status == 400:
                    raise BadRequest(response.text)
                elif response.status == 401:
                    if "WWW-Authenticate" in response.headers:
                        raise InvalidAccessToken(response.json())
                    else:
                        raise Unauthorized(response.json())
                elif response.status == 403:
                    if b"Rate Limit Exceeded" in response.content:
                        remaining = str(
                            response.headers.get("X-Rate-Limit-Remaining", "Unknown")
                        )
                        raise RateLimitExceeded(
                            "Rate Limit Exceeded. X-Rate-Limit-Remaining: {}".format(remaining)
                        )
                    else:
                        raise Forbidden(response.text)
                elif response.status == 404:
                    raise ResourceDoesNotExist("Not Found")
                elif response.status == 409:
                    raise Conflict(response.text)
                elif response.status == 422:
                    raise UnprocessableEntity(response.text)
                elif response.status > 400:
                    # generic catch-all for error codes
                    raise Exception(
                        "Encountered an error: status code {}".format(response.status)
                    )

                return response

            except aiohttp.ClientError as e:
                # Handle client-side issues, such as network errors, DNS errors, etc.
                print(f"Client error occurred: {e}")
            except asyncio.TimeoutError:
                # Handle timeout error
                print("Request timed out")
            except Exception as e:
                # Handle other exceptions
                print(f"An unexpected error occurred: {e}")

    async def apply_rate_limit_pullback(self):
        if self.rate_limit_remaining <= self.rate_limit_threshold:
            delay = self.calculate_delay()
            await asyncio.sleep(delay)

    def calculate_delay(self):
        if self.rate_limit_remaining <= 0:
            raise Exception('Rate limit exceeded')

        rate_ratio = self.rate_limit_remaining / self.rate_limit_threshold
        delay = -math.log(rate_ratio) if rate_ratio > 0 else float('inf')
        return max(0, delay)
