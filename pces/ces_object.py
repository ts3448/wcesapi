from typing import Any, Dict, Hashable, Optional

import pandas as pd
import logging
from requester import Requester, HttpMethod


logger = logging.getLogger(__name__)


class CESObject:
    """
    Base class for all classes representing objects returned by the API.
    This class abstracts Pandas DataFrame, storing attributes as columns and
    values as a single row.
    """

    def __init__(
        self,
        requester: Requester,
        request_method: HttpMethod,
        api_endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initializes the CESObject with the given parameters.

        Args:
            requester (Requester): The requester instance to use for API calls.
            request_method (HttpMethod): The HTTP method to use for the request.
            api_endpoint (str): The API endpoint to call.
            params (Optional[Dict[str, Any]]): Optional query parameters for GET requests.
            data (Optional[Dict[str, Any]]): Optional data for POST, PUT requests.
        """
        self._df: pd.DataFrame = pd.DataFrame()
        self._requester = requester
        self._request_method: HttpMethod = request_method
        self._api_endpoint = api_endpoint
        self._params = params or {}
        self._data = data
        self._params["per_page"] = 100

        self._fetch_all_data()

    @property
    def df(self) -> pd.DataFrame:
        """Returns the underlying DataFrame."""
        return self._df

    def __getattr__(self, name: str) -> Any:
        """
        Custom attribute access method.

        If the attribute is a DataFrame column, returns the column data.
        If it's a method, returns a lambda function that applies the method to all rows.
        Otherwise, returns the attribute as is.

        Args:
            name (str): The name of the attribute being accessed.

        Returns:
            Any: The attribute value, column data, or a lambda function for method application.
        """
        if name in self._df.columns:
            return self._df[name].iloc[0] if len(self._df) == 1 else self._df[name]

        attr = super().__getattribute__(name)
        if callable(attr):
            return lambda *args, **kwargs: self._apply_method(name, *args, **kwargs)
        return attr

    def _apply_method(self, name: str, *args, **kwargs):
        """
        Applies a method to all rows in the DataFrame.

        Args:
            name (str): The name of the method to apply.
            *args: Variable length argument list for the method.
            **kwargs: Arbitrary keyword arguments for the method.

        Returns:
            Union[CESObject, List[Any]]: A new CESObject if all results are CESObjects,
            otherwise a list of results or a single result if there's only one.
        """
        results = [
            getattr(self._row_to_obj(row), name)(*args, **kwargs)
            for _, row in self._df.iterrows()
        ]
        if results and all(isinstance(result, CESObject) for result in results):
            return self._combine_results(pd.concat([r.df for r in results]))
        return results[0] if len(results) == 1 else results

    def _row_to_obj(self, row: pd.Series) -> "CESObject":
        """
        Converts a single DataFrame row to a new CESObject.

        Args:
            row (pd.Series): A single row from the DataFrame.

        Returns:
            CESObject: A new CESObject instance containing only the data from the given row.
        """
        obj = type(self)(
            self._requester,
            self._request_method,
            self._api_endpoint,
            self._params,
            self._data,
        )
        obj._df = pd.DataFrame([row])
        return obj

    def _combine_results(self, combined_df: pd.DataFrame) -> "CESObject":
        """
        Combines multiple DataFrame results into a single CESObject.

        Args:
            combined_df (pd.DataFrame): A DataFrame containing combined results.

        Returns:
            CESObject: A new CESObject instance containing the combined DataFrame.
        """
        obj = type(self)(
            self._requester,
            self._request_method,
            self._api_endpoint,
            self._params,
            self._data,
        )
        obj._df = combined_df
        return obj

    def __repr__(self) -> str:
        """Provides a detailed string representation of the object."""
        classname = self.__class__.__name__
        data_str = self._df.__repr__()
        return f"{classname}:\n{data_str}"

    def __str__(self) -> str:
        """Provides a string representation of the DataFrame."""
        return self._df.__str__()

    def __iter__(self):
        """Allows iteration over the object's data."""
        yield from self._df.itertuples(index=False)

    def _fetch_all_data(self) -> None:
        """Fetches all available data, handling pagination and converting date columns."""
        next_url = self._api_endpoint
        while next_url:
            response = self._requester.request(
                self._request_method, next_url, params=self._params, data=self._data
            )
            data = response

            result_list = data.get("resultList", [])
            new_df = pd.DataFrame(result_list)
            self._df = pd.concat([self._df, new_df], ignore_index=True)

            page = data.get("page")
            page_size = data.get("pageSize")
            if page_size == len(result_list) and page is not None:
                next_url = next_url.replace(f"page={page}", f"page={page + 1}")
            else:
                next_url = None

        self._convert_date_columns()

    def _convert_date_columns(self) -> None:
        """Converts date columns to datetime objects."""
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
            "submitDate",
        ]
        for col in date_columns:
            if col in self._df.columns:
                self._df[col] = pd.to_datetime(self._df[col], errors="coerce")

    @property
    def data(self) -> Dict[Hashable, Any]:
        """Returns a dictionary representation of the object's data."""
        return self._df.to_dict(orient="records")[0] if not self._df.empty else {}

    # def get_context(self, return_type: str) -> "CESObject":
    #     """
    #     Retrieve the context (object) based on the return_type.
    #     Recursively called until the context is None (only true of the CES class).

    #     Args:
    #         return_type (str): Name of the class to return.

    #     Returns:
    #         CESObject: The object with name that matches the return_type.

    #     Raises:
    #         ValueError: If the context of the specified type is not found.
    #     """
    #     if return_type == type(self).__name__:
    #         return self
    #     elif self._config.context:
    #         return self._config.context.get_context(return_type)
    #     else:
    #         raise ValueError(
    #             f"Context of type '{return_type}' not found in the method chain."
    #         )

    # def refresh(self) -> None:
    #     """Refreshes the object's data from the API."""
    #     try:
    #         response = self._config.requester.request(
    #             self._config.request_method, self._config.first_url, **self._next_params
    #         )
    #         self._set_attributes(response.json())
    #     except Exception as e:
    #         logger.error(f"Error refreshing data: {str(e)}")
    #         raise

    # @lru_cache(maxsize=128)
    # def _apply_filters(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
    #     """Applies filters to the DataFrame. Results are cached for performance."""
    #     if not filters:
    #         return df

    #     mask = pd.Series([True] * len(df))
    #     for key, values in filters.items():
    #         if key not in df.columns:
    #             logger.warning(f"DataFrame does not have a column named {key}")
    #             continue

    #         key_mask = pd.Series([False] * len(df))
    #         for value in values:
    #             key_mask |= self._apply_single_filter(df[key], value)
    #         mask &= key_mask

    #     return df[mask].reset_index(drop=True)

    # @staticmethod
    # def _apply_single_filter(series: pd.Series, filter_value: str) -> pd.Series:
    #     """Applies a single filter to a Series."""
    #     operators_pattern = re.compile(r"^([><≥≤!=≠<>]+)")
    #     operator_match = operators_pattern.match(filter_value)
    #     operator = operator_match.group(0) if operator_match else None
    #     value = re.sub(operators_pattern, "", filter_value)

    #     try:
    #         numeric_value = float(value)
    #         return CESObject._apply_numeric_filter(series, operator, numeric_value)
    #     except ValueError:
    #         return CESObject._apply_string_filter(series, operator, value)

    # @staticmethod
    # def _apply_numeric_filter(
    #     series: pd.Series, operator: Optional[str], value: float
    # ) -> pd.Series:
    #     """Applies a numeric filter to a Series."""
    #     if operator in [">", "≥"]:
    #         return series > value
    #     elif operator in ["<", "≤"]:
    #         return series < value
    #     elif operator in ["!=", "≠", "<>"]:
    #         return series != value
    #     else:
    #         return series == value

    # @staticmethod
    # def _apply_string_filter(
    #     series: pd.Series, operator: Optional[str], value: str
    # ) -> pd.Series:
    #     """Applies a string filter to a Series."""
    #     if operator in ["!=", "≠", "<>"]:
    #         return ~series.str.match(f'^{value.replace("*", ".*")}$')
    #     else:
    #         return series.str.match(f'^{value.replace("*", ".*")}$')
