import re
import pandas as pd


class PandanatedList(object):
    """
    Abstracts both pagination of the CES API and the Pandas DataFrame object.
    """

    @property
    def df(self):
        self._grow_until_complete()
        return self._df

    def __str__(self):
        return str(self.df)

    def __getattr__(self, name):
        # ensure all the data is available
        self._grow_until_complete()

        if name in self.__dict__:
            return self.__dict__[name]

        if hasattr(self._content_class, name) and callable(getattr(self._content_class, name)):
            def method(*args, **kwargs):
                results = []
                # Extract the return_type argument
                return_type = kwargs.pop('return_type', None)

                for _, row in self.df.iterrows():
                    # Pass the current PaginatedList as the context
                    obj = self._content_class(self._requester, row.to_dict(), context=self._context)
                    result = getattr(obj, name)(*args, **kwargs)

                    if return_type:
                        context_result = obj.get_context(return_type)
                        if context_result:
                            results.append(context_result.dataframe)
                        continue

                    if isinstance(result, PandanatedList):
                        results.append(result.df)
                    elif isinstance(result, object):
                        results.append(result.dataframe)

                return pd.concat(results, ignore_index=True)
            return method
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def __init__(
        self,
        content_class,
        requester,
        request_method,
        first_url,
        filters=None,
        extra_attribs=None,
        context=None,
        **kwargs
    ):
        self._df = pd.DataFrame()
        self._filters = filters or {}
        self._context = context

        self._requester = requester
        self._content_class = content_class
        self._first_url = first_url
        self._first_params = kwargs or {}
        self._first_params["page"] = kwargs.get("page", 1)
        self._next_url = first_url
        self._next_params = self._first_params
        self._extra_attribs = extra_attribs or {}
        self._request_method = request_method
        self._fetched_complete = False

        # Make the initial API call to populate the DataFrame with the first page of data
        self._grow()

    def __iter__(self):
        for _, row in self.df.iterrows():
            yield row

    def __repr__(self):
        return "<PandanatedList of type {}>".format(self._content_class.__name__)

    def _get_next_page(self):
        response = self._requester.request(
            self._request_method,
            self._next_url,
            **self._next_params,
        )
        data = response.json()
        self._next_url = None

        # Extract the page, pageSize, and resultList from the response
        page = data.get("page")
        pageSize = data.get("pageSize")
        resultList = data.get("resultList", [])

        # Determine if there's a next page based on the condition
        if pageSize == len(resultList) and page is not None:
            # Construct the next URL by incrementing the page number
            self._next_url = re.sub(r'page=\d+', f'page={page + 1}', self._next_url)

        content = []

        for element in resultList:
            if element is not None:
                content.append(element)

        new_df = pd.DataFrame(content)

        # If there are extra attributes, add them as new columns
        if self._extra_attribs:
            for key, value in self._extra_attribs.items():
                new_df[key] = value

        return new_df

    def _grow(self):
        new_elements = self._get_next_page()
        if self._filters:
            new_elements = self.apply_filters(new_elements, self._filters)
        new_df = pd.DataFrame(new_elements)
        self.df = pd.concat([self.df, new_df], ignore_index=True)

    def _has_next(self):
        return self._next_url is not None

    def _grow_until_complete(self):
        if not self._fetched_complete:
            while self._has_next():
                self._grow()
            self._fetched_complete = True

    def apply_filters(self, df, filters):
        operators_pattern = re.compile(r'^([><≥≤!=≠<>]+)')

        # Helper function to determine if a value is numeric
        def is_numeric(value):
            try:
                float(value)
                return True
            except ValueError:
                return False

        # Helper function to handle numeric filters
        def handle_numeric_filter(series, filter_value):
            operator_match = operators_pattern.match(filter_value)
            operator = operator_match.group(0) if operator_match else None
            numeric_value = float(re.sub(operators_pattern, '', filter_value))

            if operator in ['>', '≥']:
                return series > numeric_value
            elif operator in ['<', '≤']:
                return series < numeric_value
            elif operator in ['!=', '≠', '<>']:
                return series != numeric_value
            else:
                return series == numeric_value

        # Helper function to handle non-numeric filters
        def handle_non_numeric_filter(series, filter_value):
            regex_pattern = '^' + filter_value.replace('*', '.*') + '$'
            return series.str.match(regex_pattern)

        # If filters is empty, return the original DataFrame
        if not filters:
            return df

        positive_masks = []
        negative_masks = []

        for filter_key, filter_values in filters.items():
            if filter_key not in df.columns:
                print(f"DataFrame does not have a column named {filter_key}")
                continue

            for filter_value in filter_values:
                if is_numeric(re.sub(operators_pattern, '', filter_value)):
                    positive_masks.append(handle_numeric_filter(df[filter_key], filter_value))
                else:
                    if filter_value.startswith(('!=', '≠', '<>')):
                        negative_masks.append((filter_key, re.sub(operators_pattern, '', filter_value)))
                    else:
                        positive_masks.append(handle_non_numeric_filter(df[filter_key], filter_value))

        # Combine all positive masks with 'or'
        final_positive_mask = pd.Series([False] * len(df))
        for mask in positive_masks:
            final_positive_mask |= mask

        # Only consider rows that passed the positive filters for the negative filtering
        filtered_df = df[final_positive_mask].reset_index(drop=True)

        # Combine all negative masks with 'and' within a key but 'or' between keys
        for key, neg_value in negative_masks:
            neg_mask = ~handle_non_numeric_filter(filtered_df[key], neg_value)
            filtered_df = filtered_df[neg_mask].reset_index(drop=True)

        return filtered_df.reset_index(drop=True)
