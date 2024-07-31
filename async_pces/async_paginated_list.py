import asyncio


class AsyncPaginatedList(object):
    """
    A class for handling paginated API responses asynchronously.

    Each object in the list is an instance of the `obj_class` parameter passed at creation.
    """

    def __getitem__(self, index):
        assert isinstance(index, (int, slice))
        # Directly return the item or slice from _elements
        return self._elements[index]

    def __init__(
        self,
        content_class,
        requester,
        request_method,
        first_url,
        extra_attribs=None,
        _root=None,
        _url_override=None,
        **kwargs
    ):
        self._elements = list()

        self._requester = requester
        self._content_class = content_class
        # self._per_page = 100
        self._first_url = first_url
        self._first_params = kwargs or {}
        # self._first_params["per_page"] = kwargs.get("per_page", self._per_page)
        self._next_url = first_url
        self._next_params = self._first_params
        self._extra_attribs = extra_attribs or {}
        self._request_method = request_method
        self._root = _root
        self._url_override = _url_override
        self._fetch_complete = False
        self._batch_size = 1
        self._start_page = 1

    @classmethod
    async def create(cls,
                     content_class,
                     requester,
                     request_method,
                     first_url,
                     extra_attribs=None,
                     root=None,
                     _url_override=None,
                     **kwargs):
        obj = cls(content_class,
                  requester,
                  request_method,
                  first_url,
                  extra_attribs,
                  root,
                  _url_override,
                  **kwargs)
        await obj._initialize()
        return obj

    async def _initialize(self):
        # Perform initial async fetching here, for instance, fetching the first page
        await self._fetch_all()

    def __iter__(self):
        for element in self._elements:
            yield element

    def __repr__(self):
        return "<PaginatedList of type {}>".format(self._content_class.__name__)
    
    def __len__(self):
        return len(self._elements)
    
    async def _fetch_batch(self, start_page, batch_size):
        tasks = []
        for i in range(batch_size):
            page_url = self._construct_next_page_url(self._first_url, start_page + i)
            tasks.append(asyncio.create_task(self._fetch_page(page_url)))

        batch_results = await asyncio.gather(*tasks)
        for content, length in batch_results:
            if length < self._per_page:  # Or any other threshold you want to use
                self._fetch_complete = True
            if content:
                self._elements.extend(content)

    def _construct_next_page_url(self, url, current_page):
        # Check if the URL already has query parameters
        if '?' in url:
            # URL already has query parameters, append with '&'
            updated_url = "{}&page={}".format(url, current_page)
        else:
            # URL has no query parameters, append with '?'
            updated_url = "{}?page={}".format(url, current_page)

        return updated_url

    async def _fetch_page(self, page_url):
        response = await self._requester.request(
            self._request_method,
            page_url,
            _url=self._url_override,
            **self._next_params,
        )
        data = await response.json()
        content = []
        if self._root:
            try:
                data = data[self._root]
            except KeyError:
                raise ValueError(
                    "The key <{}> does not exist in the response.".format(self._root)
                )
        for element in data:
            if element is not None:
                element.update(self._extra_attribs)
                content.append(self._content_class(self._requester, element))

        return content, len(content)

    async def _fetch_all(self):
        start_page = self._start_page
        batch_size = self._batch_size

        while not self._fetch_complete:
            await self._fetch_batch(start_page, batch_size)
            batch_size = 10
            start_page += batch_size
