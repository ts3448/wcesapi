import re
import pandas as pd


class CESObject(object):
    """
    Base class for all classes representing objects returned by the API.

    This class abstracts Pandas DataFrame, storing attributes as columns and
    values as a single row.
    """

    @property
    def df(self):
        return self._df

    def __getattr__(self, name):
        # Check if attribute exists in the main dataframe
        if name in self._df.columns:
            return self._df[name].iloc[0]

        # If attribute doesn't exist, raise an AttributeError
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'")

    def __init__(self,
                 requester,
                 attributes,
                 content_class,
                 request_method,
                 first_url,
                 filters=None,
                 extra_attribs=None,
                 context=None,
                 skip_request=False,
                 join=False,
                 **kwargs):
        """
        Initializes the class, makes at least the first API call, and calls "set_attributes".

        Args:
            requester (Requester): The Requester object used to make API calls.

            attributes (json): JSON formatted response from the API call.

            context (object): The object that called the method that created
                the current object. Used to navigate through chained methods
                to return a specific object, rather than the last object
                called in the chain.

        Returns:
            CESObject: Instance of the class.

        """
        self._df = pd.DataFrame()
        self._filters = filters or {}
        self._context = context

        self._requester = requester
        self._requester = requester
        self._content_class = content_class
        self._first_url = first_url
        self._first_params = kwargs or {}
        self._first_params["per_page"] = kwargs.get("per_page", 100)
        self._next_url = first_url
        self._next_params = self._first_params
        self._extra_attribs = extra_attribs or {}
        self._request_method = request_method
        self._fetched_complete = False
        self._join = join
        self._shared_columns = {}

        self._set_attributes(attributes)

    def __repr__(self): 
        classname = self.__class__.__name__

        # Extracting column names from the DataFrame
        attrs = ", ".join(self._df.columns)

        return "{}({})".format(classname, attrs)

    def __iter__(self):
        for _, row in self._df.iterrows():
            yield row

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
            new_elements = self._apply_filters(new_elements, self._filters)
        new_df = pd.DataFrame(new_elements)
        self._df = pd.concat([self._df, new_df], ignore_index=True)

    def _has_next(self):
        return self._next_url is not None

    def _grow_until_complete(self):
        if not self._fetched_complete:
            while self._has_next():
                self._grow()
            self._fetched_complete = True

    def _apply_filters(self, df, filters):
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

    def _set_attributes(self, attributes):
        """
        Load the JSON response (dict) into a DataFrame with attributes
        as columns and data as a single row.

        Params:
            attributes (dict): The JSON object used to create the object data.

        """
        # Check if 'resultList' key exists in attributes
        if 'resultList' in attributes:
            # Use the resultList for the dataframe
            self._df = pd.DataFrame(attributes['resultList'])
        else:
            self._df = pd.DataFrame([attributes])

        # Convert specific columns to datetime format
        date_columns = [
            "created",
            "updated",
            "startDate",
            "endDate",
            "adminReportAccessStartDate",
            "adminReportAccessEndDate",
            "instructorReportAccessStartDate",
            "instructorReportAccessEndDate",
            "taReportAccessStartDate",
            "taReportAccessEndDate",
            "customQuestionStartDate",
            "customQuestionEndDate",
            "submitDateTime",
            "courseSurveyStart",
            "courseSurveyEnd",
            "submitDate"
            ]
        for col in date_columns:
            if col in self._df.columns:
                self._df[col] = pd.to_datetime(self._df[col])

    def get_context(self, return_type):
        """
        Retrieve the context (object) based on the return_type.
        Recursively called until the context is None (only true
        of the CES class).

        Params:
            return_type (str): Name of the class to return.
            join (bool): Whether to join the dataframes or not.

        Returns:
            self (object): The object with name that matches the return_type.
        """

        if return_type == type(self).__name__:
            return self
        elif self._context:
            return self._context.get_context(return_type)
        else:
            raise ValueError(
                "Context of type '{}' not found in the method chain."
                ).format(return_type)
