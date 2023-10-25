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

    def __getattr__(self, name):
        # ensure all the data is available
        self._grow_until_complete()

        if name in self.__dict__:
            return self.__dict__[name]

        if hasattr(self._content_class, name) and callable(getattr(self._content_class, name)):
            def method(*args, **kwargs):

                content_class = None
                result_is_pandanated = False
                result_is_content_class = False
                results = []
                return_type = kwargs.pop('return_type', None)

                for index, row in self._df.iterrows():
                    # Pass the current PaginatedList as the context
                    obj = self._content_class(self._requester, row.to_dict(), context=self._context)

                    # this is the result of the method call made on the
                    # _content_class using the provided method and arguments.
                    result = getattr(obj, name)(*args, **kwargs)

                    # on the first pass, determine if the result class will be
                    # a PandanatedList or a single instance of whatever class
                    # _content_class is.
                    if index == 0:
                        result_is_pandanated = isinstance(result, PandanatedList)
                        result_is_content_class = isinstance(result, object) and not result_is_pandanated
                        context_result = result._context

                    # if the resulting dataframe is empty, do not append
                    # the result data
                    if result._df.empty:
                        continue

                    if result_is_pandanated:
                        # if there is a return_type
                        if return_type:
                            context_result = obj.get_context(return_type)
                            if context_result:
                                results.append(context_result._df)
                                content_class = type(context_result)
                            continue

                        results.append(result._df)
                        content_class = result._content_class

                    elif result_is_content_class:
                        if return_type:
                            context_result = obj.get_context(return_type)
                            if context_result:
                                results.append(context_result._df)
                                content_class = type(context_result)
                            continue

                        results.append(result._df)
                        content_class = type(result)
                    else:
                        raise ValueError("Unsupported response type.")

                concat_results = pd.concat(results, ignore_index=True)
                pandanated_list_results = PandanatedList(
                    content_class,
                    self._requester,
                    request_method=None,
                    first_url=None,
                    context=context_result,
                    skip_request=True)
                pandanated_list_results._df = concat_results
                pandanated_list_results._fetched_complete = True
                return pandanated_list_results
            return method
        raise AttributeError("Neither '{}' nor {} have an attribute '{}'"
                             .format(type(self).__name__, self._content_class, name))

    def __init__(
        self,
        content_class,
        requester,
        request_method,
        first_url,
        filters=None,
        extra_attribs=None,
        context=None,
        skip_request=False,
        join=False,
        **kwargs
    ):
        self._df = pd.DataFrame()
        self._filters = filters or {}
        self._context = context

        self._requester = requester
        self._content_class = content_class
        self._first_url = first_url
        self._first_params = kwargs or {}
        self._first_params["page"] = kwargs.get("page", 100)
        self._next_url = first_url
        self._next_params = self._first_params
        self._extra_attribs = extra_attribs or {}
        self._request_method = request_method
        self._fetched_complete = False
        self._join = join

        # Make the initial API call to populate the DataFrame with the first page of data
        if not skip_request:
            self._grow()

    def __iter__(self):
        for _, row in self._df.iterrows():
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
        self._df = pd.concat([self._df, new_df], ignore_index=True)

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

    def prefix_columns(self, df):
        """
        Returns a DataFrame with prefixed columns, based on the lowercase name of the class.
        """
        prefix = f"{type(self).__name__.lower()}_"
        new_df = df.copy()
        new_df.columns = [prefix + col for col in new_df.columns]
        return new_df

    def join_contexts(self, column_mappings={}, method="inner"):
        """
        Joins the DataFrame with the DataFrame in its context based on the provided column mappings.
        Returns a new DataFrame.
        """

        # Prefix the current dataframe's columns
        prefixed_df = self.prefix_columns(self._df)

        # Start with the current dataframe copy
        result_df = prefixed_df

        # Check if the object has a context and that context has a dataframe
        if hasattr(self, "_context") and self._context and hasattr(self._context, "df"):

            # Get the appropriate column mapping for this object
            columns_for_join = column_mappings.get(type(self).__name__, {})

            # Extract the columns to join on for current and context dataframes
            # and prefix them with their respective class names
            self_columns = [f"{type(self).__name__.lower()}_{col}" for col in columns_for_join.keys()]
            context_columns = [f"{type(self._context).__name__.lower()}_{col}" for col in columns_for_join.values()]

            # Prefix the context dataframe's columns without altering the original
            context_prefixed_df = self._context.prefix_columns(self._context._df)

            # Join with the context's dataframe using the specified columns
            if self_columns and context_columns:
                result_df = result_df.merge(context_prefixed_df, left_on=self_columns, right_on=context_columns, how=method)

            # Recursive call: Join with the resulting dataframe from the context's join_contexts method
            context_join_df = self._context.join_contexts(column_mappings=column_mappings, method=method)
            result_df = result_df.merge(context_join_df, left_on=self_columns, right_on=context_columns, how=method)

        return result_df